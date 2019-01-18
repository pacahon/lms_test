from crispy_forms.bootstrap import TabHolder, Tab, PrependedText, FormActions, \
    StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Fieldset
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from core.admin import CityAwareModelForm, CityAwareSplitDateTimeField
from core.models import LATEX_MARKDOWN_HTML_ENABLED
from core.widgets import UbereditorWidget, DateInputAsTextInput, \
    TimeInputAsTextInput, CityAwareSplitDateTimeWidget
from courses.models import Course, CourseNews, MetaCourse, Venue, CourseClass, \
    Assignment
from courses.settings import ClassTypes
from core.forms import CANCEL_SAVE_PAIR
from core.constants import DATE_FORMAT_RU, TIME_FORMAT_RU

DROP_ATTACHMENT_LINK = '<a href="{}"><i class="fa fa-trash-o"></i>&nbsp;{}</a>'


class CourseEditDescrForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab(
                    'RU',
                    'description_ru',
                ),
                Tab(
                    'EN',
                    'description_en',
                ),
                template='crispy_forms/square_tabs.html'
            ),
            CANCEL_SAVE_PAIR)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Course
        fields = ['description_ru', 'description_en']
        widgets = {
            'description_ru': UbereditorWidget,
            'description_en': UbereditorWidget,
        }


class CourseNewsForm(forms.ModelForm):
    title = forms.CharField(
        label=_("Title"),
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off',
                                      'autofocus': 'autofocus'}))
    text = forms.CharField(
        label=_("Text"),
        help_text=LATEX_MARKDOWN_HTML_ENABLED,
        required=True,
        widget=UbereditorWidget)

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div('title', 'text'),
            CANCEL_SAVE_PAIR)
        super().__init__(*args, **kwargs)
        if course:
            self.instance.course = course

    class Meta:
        model = CourseNews
        fields = ['title', 'text']


class CourseForm(forms.ModelForm):
    name_ru = forms.CharField(
        label=_("Course|name"),
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off',
                                      'autofocus': 'autofocus'}))
    description_ru = forms.CharField(
        label=_("Course|description"),
        required=True,
        help_text=LATEX_MARKDOWN_HTML_ENABLED,
        widget=UbereditorWidget)

    @property
    def helper(self):
        helper = FormHelper()
        helper.layout = Layout(
            TabHolder(
                Tab(
                    'RU',
                    'name_ru',
                    'description_ru',
                ),
                Tab(
                    'EN',
                    'name_en',
                    'description_en',
                ),
            ),
            CANCEL_SAVE_PAIR)
        return helper

    class Meta:
        model = MetaCourse
        fields = ['name_ru', 'name_en', 'description_ru', 'description_en']


class CourseClassForm(forms.ModelForm):
    venue = forms.ModelChoiceField(
        queryset=Venue.objects.all(),
        label=_("Venue"),
        empty_label=None)
    type = forms.ChoiceField(
        label=_("Type"),
        choices=ClassTypes.choices)
    name = forms.CharField(
        label=_("CourseClass|Name"),
        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    description = forms.CharField(
        label=_("Description"),
        required=False,
        help_text=LATEX_MARKDOWN_HTML_ENABLED,
        widget=UbereditorWidget(attrs={'autofocus': 'autofocus'}))
    slides = forms.FileField(
        label=_("Slides"),
        required=False,
        widget=forms.ClearableFileInput)
    attachments = forms.FileField(
        label=_("Attached files"),
        required=False,
        help_text=_("You can select multiple files"),
        widget=forms.ClearableFileInput(attrs={'multiple': 'multiple'}))
    other_materials = forms.CharField(
        label=_("Other materials"),
        required=False,
        help_text=LATEX_MARKDOWN_HTML_ENABLED,
        widget=UbereditorWidget)
    date = forms.DateField(
        label=_("Date"),
        help_text=_("Format: dd.mm.yyyy"),
        widget=DateInputAsTextInput(attrs={'class': 'datepicker',
                                           'autocomplete': 'off'}))
    starts_at = forms.TimeField(
        label=_("Starts at"),
        help_text=_("Format: hh:mm"),
        widget=TimeInputAsTextInput(format="%H:%M",
                                    attrs={'autocomplete': 'off'}))
    ends_at = forms.TimeField(
        label=_("Ends at"),
        help_text=_("Format: hh:mm"),
        widget=TimeInputAsTextInput(format="%H:%M",
                                    attrs={'autocomplete': 'off'}))

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        assert course is not None
        if "instance" in kwargs:
            remove_links = "<ul class=\"list-unstyled __files\">{0}</ul>".format(
                "".join("<li>{}</li>".format(
                            DROP_ATTACHMENT_LINK.format(
                                attachment.get_delete_url(),
                                attachment.material_file_name))
                        for attachment
                        in kwargs["instance"].courseclassattachment_set.all()))
        else:
            remove_links = ""
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(Div('type', css_class='col-xs-2'),
                Div('venue', css_class='col-xs-3'),
                css_class='row'),
            Div('name',
                'description',
                css_class="form-group"),
            Div(Div(PrependedText('date', '<i class="fa fa-calendar"></i>'),
                    HTML("&nbsp;"),
                    PrependedText('starts_at', '<i class="fa fa-clock-o"></i>'),
                    HTML("&nbsp;"),
                    PrependedText('ends_at', '<i class="fa fa-clock-o"></i>'),
                    css_class="form-inline"),
                css_class="form-group"),
            Fieldset(_("Materials"),
                     Div(
                         Div('slides', css_class='col-xs-6'),
                         Div('attachments', HTML(remove_links),
                             css_class='col-xs-6'),
                         css_class='row'
                     ),
                     'video_url',
                     'other_materials'),
            FormActions(
                StrictButton(_('<i class="fa fa-plus"></i> Save and add'),
                             name='_addanother', type="submit",
                             css_class="btn-primary btn-outline"),
                CANCEL_SAVE_PAIR
            )
        )
        super().__init__(*args, **kwargs)
        self.fields['venue'].queryset = self.fields['venue'].queryset.filter(
            city_id=course.city_id)
        self.instance.course = course

    class Meta:
        model = CourseClass
        fields = ['venue', 'type', 'name', 'description',
                  'slides', 'attachments', 'video_url', 'other_materials',
                  'date', 'starts_at', 'ends_at']

    def clean_date(self):
        date = self.cleaned_data['date']
        # Validate this since 'course' could be invalid
        if 'course' in self.cleaned_data:
            course = self.cleaned_data['course']
            semester_start = course.semester.starts_at.date()
            semester_end = course.semester.ends_at.date()
            assert semester_start <= semester_end
            if not semester_start <= date <= semester_end:
                raise ValidationError(
                    _("Inconsistent with this course's "
                      "semester (from %(starts_at)s to %(ends_at)s)"),
                    code='date_out_of_semester',
                    params={'starts_at': semester_start,
                            'ends_at': semester_end})
        return date


class AssignmentForm(CityAwareModelForm):
    title = forms.CharField(
        label=_("Title"),
        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    text = forms.CharField(
        label=_("Text"),
        help_text=LATEX_MARKDOWN_HTML_ENABLED,
        widget=UbereditorWidget(attrs={'autofocus': 'autofocus'}))
    deadline_at = CityAwareSplitDateTimeField(
        label=_("Deadline"),
        input_date_formats=[DATE_FORMAT_RU],
        input_time_formats=[TIME_FORMAT_RU],
        widget=CityAwareSplitDateTimeWidget(date_format=DATE_FORMAT_RU,
                                            time_format=TIME_FORMAT_RU)
    )
    attachments = forms.FileField(
        label=_("Attached file"),
        required=False,
        help_text=_("You can select multiple files"),
        widget=forms.ClearableFileInput(attrs={'multiple': 'multiple'}))
    is_online = forms.BooleanField(
        label=_("Can be passed online"),
        required=False)
    passing_score = forms.IntegerField(
        label=_("Passing score"),
        initial=2)
    maximum_score = forms.IntegerField(
        label=_("Maximum score"),
        initial=5)

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        assert course is not None
        if "instance" in kwargs:
            instance = kwargs["instance"]
            remove_links = "<ul class=\"list-unstyled __files\">{0}</ul>".format(
                "".join("<li>{}</li>".format(
                    DROP_ATTACHMENT_LINK.format(aa.get_delete_url(),
                                                aa.file_name))
                        for aa in instance.assignmentattachment_set.all()))
        else:
            remove_links = ""
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                'title',
                'text',
                Div(
                    Div('deadline_at', css_class='col-xs-6'),
                    Div('attachments', HTML(remove_links),
                        css_class='col-xs-6'),
                    css_class='row'
                ),
                Div(
                    Div('passing_score',
                        'maximum_score',
                        css_class="form-inline"),
                    css_class="form-group"
                ),
                'is_online',
                css_class="form-group"
            ),
            CANCEL_SAVE_PAIR)
        super().__init__(*args, **kwargs)
        self.instance.course = course

    class Meta:
        model = Assignment
        fields = ['title', 'text', 'deadline_at', 'attachments', 'is_online',
                  'passing_score', 'maximum_score']