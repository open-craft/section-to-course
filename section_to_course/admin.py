"""
Admin views for creating and managing section-based courses.
"""
import json

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import SELECT2_TRANSLATIONS, AutocompleteSelect
from django.core import validators
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django_object_actions import DjangoObjectActions
from opaque_keys import InvalidKeyError
from opaque_keys.edx.locator import BlockUsageLocator, CourseLocator

from .compat import (
    course_exists,
    create_course,
    get_course_outline,
    organization_options,
    sequence_does_not_exist_exception,
)
from .models import SectionToCourseLink
from .utils import paste_from_template


class ArbitraryAutocompleteSelect(AutocompleteSelect):
    """
    Autocomplete field for an arbitrary endpoint.
    """

    def __init__(self, field_name, admin_site=None, attrs=None, choices=(), using=None):
        """
        Initialize field with context.

        We don't use admin_site, so shim this function to allow it to be None.
        We also don't use the fully featured field, electing to request a field name instead.
        """
        self.field_name = field_name
        super().__init__(None, admin_site, attrs=attrs, choices=choices, using=using)

    def get_url(self):
        """Replace this with your own URL generating function."""
        raise NotImplementedError

    def optgroups(self, name, value, attr=None):
        """
        We don't use optgroups, so we need to return a dummy value to satisfy the upstream code.
        """
        return [(None, [], 0)]

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Set select2's AJAX attributes.

        Attributes can be set using the html5 data attribute.
        Nested attributes require a double dash as per
        https://select2.org/configuration/data-attributes#nested-subkey-options
        """
        attrs = forms.Select.build_attrs(self, base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault('class', '')
        attrs.update({
            'data-ajax--cache': 'true',
            'data-ajax--delay': 250,
            'data-ajax--type': 'GET',
            'data-ajax--url': self.get_url(),
            'data-theme': 'admin-autocomplete',
            'data-allow-clear': json.dumps(not self.is_required),
            'data-placeholder': '',  # Allows clearing of the input.
            'class': attrs['class'] + (' ' if attrs['class'] else '') + 'admin-autocomplete',
        })
        return attrs


class SectionAutocompleteSelect(ArbitraryAutocompleteSelect):
    """
    Widget which will autocomplete section IDs.
    """

    def __init__(self, *args, course_field=None, **kwargs):
        """
        Set up the custom course_field argument, so we can use JS to dynamically generate the required URL.
        """
        if course_field is None:
            raise TypeError('You must pair section autocomplete with a field containing a course key.')
        self.course_field = course_field
        super().__init__(*args, **kwargs)

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Build the widget attributes.
        """
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        # Always start disabled. JS will enable the field if it is appropriate to do so.
        attrs['disabled'] = 'true'
        attrs['data-url-template'] = self.get_url()
        # If this attribute is present, it is impossible to overwrite with a dynamic URL generating function
        # on the front end.
        del attrs['data-ajax--url']
        attrs['data-course-field'] = f'id_{self.course_field}'
        # Replace with our own indicator class so that we can invoke select2 with our own custom options.
        attrs['class'] += ' course-section-autocomplete'
        return attrs

    def get_url(self):
        """
        Get URL for autocomplete lookup.

        Start with a bogus form of the URL. We'll use JS to update it with a real version when the parent
        field has been filled with a course key.
        """
        return reverse('section_to_course:section_autocomplete', kwargs={'course_id': '<course_id>'})

    @property
    def media(self):
        """
        Gather the static assets required for our autocomplete field.
        """
        extra = '' if settings.DEBUG else '.min'
        i18n_name = SELECT2_TRANSLATIONS.get(get_language())
        i18n_file = ('admin/js/vendor/select2/i18n/%s.js' % i18n_name,) if i18n_name else ()
        return forms.Media(
            js=(
                   'admin/js/vendor/jquery/jquery%s.js' % extra,
                   'admin/js/vendor/select2/select2.full%s.js' % extra,
               ) + i18n_file + (
                   'admin/js/jquery.init.js',
                   'section_to_course/js/admin-tools.js',
               ),
            css={
                'screen': (
                    'admin/css/vendor/select2/select2%s.css' % extra,
                    'admin/css/autocomplete.css',
                ),
            },
        )


class CreateSectionToCourseLink(forms.ModelForm):
    """
    Form for creating a new section to course link.
    """

    source_course_id = forms.CharField(
        max_length=127,
    )
    source_section_id = forms.CharField(
        max_length=255,
        widget=SectionAutocompleteSelect(
            'source_section_id',
            course_field='source_course_id',
        ),
    )
    new_course_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': _('e.g. Introduction to Computer Science')}),
        help_text=_('The public display name for your course. This cannot be changed, '
                    'but you can set a different display name in Advanced Settings later.'),
    )
    new_course_org = forms.ChoiceField(
        choices=tuple(),
        help_text=_('The name of the organization sponsoring the course. Note: The organization '
                    'name is part of the course URL. This cannot be changed, but you can set a '
                    'different display name in Advanced Settings later. If your organization '
                    'is not listed, you can add it using the Organizations app settings in the '
                    'admin.'),
    )
    new_course_number = forms.SlugField(
        widget=forms.TextInput(attrs={'placeholder': _('e.g. CS101')}),
        help_text=_('The unique number that identifies your course within your organization. '
                    'Note: This is part of your course URL, so no spaces or special characters '
                    'are allowed and it cannot be changed.'),
        validators=[validators.validate_slug],
    )
    new_course_run = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('e.g. 2014_T1')}),
        help_text=_('The term in which your course will run. Note: This is part of your course '
                    'URL, so no spaces or special characters are allowed and it cannot be changed.'),
        validators=[validators.validate_slug],
    )

    def __init__(self, *args, user, **kwargs):
        """
        Initialize the form with a user.
        """
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['new_course_org'].choices = organization_options()

    def clean_source_section_id(self):
        """
        Convert the section ID into a BlockUsageLocator.
        """
        try:
            return BlockUsageLocator.from_string(self.cleaned_data.get('source_section_id', ''))
        except InvalidKeyError as err:
            raise ValidationError(str(err)) from err

    def save_m2m(self):  # pylint: disable=method-hidden
        """Shim function that allows the form to save properly."""

    def clean(self):
        """
        Validate the form, raising an error if the course key is too long or already exists.
        """
        super().clean()
        org = self.cleaned_data.get('new_course_org', '')
        number = self.cleaned_data.get('new_course_number', '')
        run = self.cleaned_data.get('new_course_run', '')
        if not all((org, number, run)):
            # Validation error will pop up elsewhere.
            return self.cleaned_data
        if len(run + number + org) > 65:
            raise ValidationError(
                _('The course key is too long. Org, number, and run must be less than 65 characters total.'),
            )
        key = CourseLocator(org, number, run)
        if course_exists(key):
            raise ValidationError(
                _('A course with this number, org, and run already exists. Please choose different values.')
            )
        return self.cleaned_data

    def save(self, *args, **kwargs):
        """
        Create the course and then copy the section into it.
        """
        cleaned_data = self.cleaned_data
        org = cleaned_data['new_course_org']
        number = cleaned_data['new_course_number']
        run = cleaned_data['new_course_run']
        course = create_course(
            user=self.user,
            org=org,
            number=number,
            run=run,
            display_name=cleaned_data['new_course_name'],
            self_paced=True,
        )
        return paste_from_template(
            destination_course_key=course.id,
            source_block_usage_key=cleaned_data['source_section_id'],
            user=self.user,
        )

    class Meta:
        """
        Meta configuration for SectionToCourse model form.
        """

        fields = (
            'source_course_id',
            'source_section_id',
            'new_course_name',
            'new_course_org',
            'new_course_number',
            'new_course_run',
        )
        model = SectionToCourseLink


@admin.action(description=_('Refresh section content from source.'))
def refresh_courses(model_admin, request, queryset):
    """Refresh selected courses in the admin."""
    for item in queryset:
        paste_from_template(
            destination_course_key=item.destination_course_id,
            source_block_usage_key=item.source_section_id,
            user=request.user,
        )
    model_admin.message_user(request, _('Refreshed {} courses successfully.').format(queryset.count()))


class SectionToCourseLinkAdmin(DjangoObjectActions, admin.ModelAdmin):
    """
    Admin view for section to course links.
    """

    list_display = ('name', 'source_course_id', 'source_section_id', 'destination_course_id', 'last_refresh', 'link')
    list_filter = ('source_course_id', 'destination_course_id')
    actions = [refresh_courses]
    change_actions = ('refresh_this', )

    def refresh_this(self, request, obj):
        """
        Refresh this course from its source via a special button on the edit page.
        """
        paste_from_template(
            destination_course_key=obj.destination_course_id,
            source_block_usage_key=obj.source_section_id,
            user=request.user,
        )
        self.message_user(request, _("Refreshed course successfully."))

    refresh_this.label = _("Refresh Course Content")
    refresh_this.short_description = _("Refresh this course's content from the source section.")

    def name(self, obj):  # pylint: disable=no-self-use
        """
        Display course name.
        """
        try:
            dest_course_outline = get_course_outline(obj.destination_course_id)
        except sequence_does_not_exist_exception():
            # Add in some resilience here in case we deleted the course.
            dest_course_outline = None
        title = (dest_course_outline and dest_course_outline.title) or str(obj.destination_course_id)
        return title

    def link(self, obj):  # pylint: disable=no-self-use
        """
        Generate a link to the course in studio for quick access.
        """
        return format_html(
            _('<a href="/course/{}">edit course</a>'),
            obj.destination_course_id,
        )

    def get_readonly_fields(self, request, obj=None):
        """
        Make fields editable based on whether we're creating a new link.
        """
        if obj is None:
            return tuple()
        # Note: Even though the names of these fields are not on the custom creation form,
        # their presence as read_only fields on the admin page causes them to be included
        # on the admin editing page. So, we only list them if we're editing an existing link.
        # At the moment, none of the fields should be modified manually, so they're all in
        # this list.
        return (
            'source_course_id',
            'destination_course_id',
            'source_section_id',
            'destination_section_id',
            'last_refresh',
            'link',
        )

    def get_form(self, request, obj, *args, **kwargs):
        """
        Change form depending on whether we're creating a new SectionToCourseLink or not.
        """
        if obj is None:
            # This violence is required because the actual instantiation form is way deep in the admin code.
            class UserAugmentedForm(CreateSectionToCourseLink):
                def __new__(cls, *args, **kwargs):
                    kwargs['user'] = request.user
                    return CreateSectionToCourseLink(*args, **kwargs)
                user = request.user
            return UserAugmentedForm
        return super().get_form(request, *args, obj=obj, **kwargs)


admin.site.register(SectionToCourseLink, SectionToCourseLinkAdmin)
