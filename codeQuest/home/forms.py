from django import forms
from home.models import CodeSubmission

LANGUAGE_CHOICES = [
    ("py", "Python"),
    ("c", "C"),
    ("cpp", "C++")
]

class CodeSubmissionForm(forms.ModelForm):
    language = forms.ChoiceField(
        choices=LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    code = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'code-editor',
            'placeholder': 'Write your code here...'
        })
    )
    input_data = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter input data here(Enter each input in different lines)...'
        })
    )
    output_data = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CodeSubmission
        fields = ["language", "code", "input_data", "output_data"]

