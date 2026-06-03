from django import forms
from .models import Submission
import os

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['full_name', 'email', 'project_title', 'description', 'file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            allowed_extensions = [
                '.pdf', '.doc', '.docx',
                '.xls', '.xlsx',
                '.ppt', '.pptx',
                '.txt', '.csv',
                '.jpg', '.jpeg', '.png',
                '.zip', '.rar',
            ]
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError('File type not allowed!')
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File too large. Maximum size is 10MB.')
        return file