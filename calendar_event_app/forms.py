from django import forms
from bootstrap3_datepicker.widgets import DatePickerInput

TYPE_CHOICES = (
    ('None', '---'),
    ('Other', 'Other'),
    ('Meeting Prep', 'Meeting Prep'),
    ('POC Prep', 'POC Prep'),
    ('Rfx', 'Rfx'),
    ('POC', 'POC'),
    ('White Boarding', 'White Boarding'),
    ('Demo/Presentation', 'Demo/Presentation'),
    ('Discovery', 'Discovery'),
    ('Followup', 'Followup'),
    ('Admin', 'Admin'),
    ('Travel', 'Travel'),
    ('BVA', 'BVA'),
    ('Develop Architecture', 'Develop Architecture'),
    ('Marketing Event', 'Marketing Event'),
    ('Training', 'Training'),
)


class AddTaskForm(forms.Form):
    activity_date = forms.DateField(widget=DatePickerInput(format="mm/dd/yyyy",
                                                           attrs={"placeholder": "Due Date",
                                                                  "class": 'form-control input-sm'})
                                    )

    subject = forms.CharField(max_length=500, required=True,
                              widget=forms.TextInput(attrs={'placeholder': 'Subject',
                                                            'class': 'form-control input-sm'})
                              )

    task_type = forms.ChoiceField(choices=TYPE_CHOICES, required=True,
                                  widget=forms.Select(attrs={'class': 'form-control input-sm',
                                                             'placeholder': ''})
                                  )

    time_spent = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Time (minutes)',
                                                                   'class': 'form-control input-sm'})
                                    )

    opportunity_id = forms.CharField(max_length=30, required=True, widget=forms.HiddenInput)

    def clean_task_type(self):
        if self.cleaned_data['task_type'] == 'None':
            raise forms.ValidationError("Please select a Task Type", code='err1')
        return self.cleaned_data['task_type']

    def clean_time_spent(self):
        if self.cleaned_data['time_spent'] <= 0:
            raise forms.ValidationError("Provide a value for time spent", code='err2')
        return self.cleaned_data['time_spent']


class ImportTaskForm(forms.Form):
    ImportRange = forms.CharField(max_length=30)


class PreferenceForm(forms.Form):
    time_zone = forms.CharField(max_length=50)