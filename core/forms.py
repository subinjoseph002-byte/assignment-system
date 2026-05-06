from django import forms
from django.contrib.auth.forms import UserCreationForm
from core.models import User, Assignment, Submission, Mark

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'role': forms.Select(attrs={'class': 'form-input'}),
        }

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'subject', 'deadline', 'file', 'marking_criteria']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'subject': forms.TextInput(attrs={'class': 'form-input'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'file': forms.FileInput(attrs={'class': 'form-input'}),
            'marking_criteria': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Optional: Add grading rules here.'}),
        }

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-input', 'accept': '.pdf,.doc,.docx'})
        }

    def clean_file(self):
        file = self.cleaned_data.get('file', False)
        if file:
            if not file.name.lower().endswith(('.pdf', '.doc', '.docx')):
                raise forms.ValidationError("Invalid file type. Only PDF and DOC/DOCX files are accepted.")
        return file

class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['marks', 'feedback']
        widgets = {
            'marks': forms.NumberInput(attrs={'class': 'form-input'}),
            'feedback': forms.Textarea(attrs={'class': 'form-input', 'rows': 3})
        }
