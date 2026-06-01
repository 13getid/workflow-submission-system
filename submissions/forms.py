from django import forms 
from .models import Submission

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = [ 'full_name','project_title','description']