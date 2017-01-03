from django import forms
from bootstrap3_datepicker.widgets import DatePickerInput
from calendar_event_app.api.clients.UserClient import UserClient
from django.conf import settings


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


class RegistrationForm(forms.Form):
    firstName = forms.CharField(max_length=100, required=True)
    lastName = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label="email")

    def clean_email(self):
        """
        email field validation to check if the username is already in Okta
        """
        email = self.cleaned_data['email']
        parts = email.split("@")
        if parts[1] != 'okta.com':
            raise forms.ValidationError("You must register with an Okta email")

        try:
            client = UserClient(''.join(['https://', settings.OKTA_ORG]), settings.API_TOKEN)
            result = client.filter_user(filter_string='profile.login eq "' + email + '"')
            readCount = len(result)
        except Exception as e:
            return self.cleaned_data['email']

        if readCount > 0:
            raise forms.ValidationError("A user with this email already exists")

        return self.cleaned_data['email']