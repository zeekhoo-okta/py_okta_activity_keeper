from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from bootstrap3_datepicker.fields import DatePickerField
from bootstrap3_datepicker.widgets import DatePickerInput

TYPE_CHOICES = (
    ('None', '---'),
    ('0', 'Other'),
    ('1', 'Meeting Prep'),
    ('2', 'POC Prep'),
    ('3', 'Rfx'),
    ('4', 'POC'),
    ('5', 'White Boarding'),
    ('6', 'Demo/Presentation'),
    ('7', 'Discovery'),
    ('8', 'Followup'),
    ('9', 'Admin'),
    ('10', 'Travel'),
    ('11', 'BVA'),
    ('12', 'Develop Architecture'),
    ('13', 'Marketing Event'),
    ('14', 'Training'),
)


class AddTaskForm(forms.Form):
    ActivityDate = forms.DateField(widget=DatePickerInput(format="mm/dd/yyyy",
                                                          attrs={"placeholder": "Due Date", "class": 'form-control input-sm'}))

    Subject = forms.CharField(max_length=500, required=True,
                              widget=forms.TextInput(attrs={'placeholder': 'Subject',
                                                            'class': 'form-control input-sm'})
                              )

    TaskType = forms.ChoiceField(choices=TYPE_CHOICES, required=True,
                                 widget=forms.Select(attrs={'class': 'form-control input-sm', 'placeholder': ''}))

    TimeSpent = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Time (minutes)',
                                                                   'class': 'form-control input-sm'})
                                   )


class ImportTaskForm(forms.Form):
    ImportRange = forms.CharField(max_length=30)