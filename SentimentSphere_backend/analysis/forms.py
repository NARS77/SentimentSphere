from django import forms
from .models import AnalysisPrompt
from dashboard.models import FeedbackBatch, FeedbackSource

class UploadBatchForm(forms.ModelForm):
    class Meta:
        model = FeedbackBatch
        fields = ['name', 'source', 'original_file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'original_file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AnalysisPromptForm(forms.ModelForm):
    class Meta:
        model = AnalysisPrompt
        fields = ['name', 'prompt_template', 'description', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'prompt_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AnalyzeBatchForm(forms.Form):
    prompt = forms.ModelChoiceField(
        queryset=AnalysisPrompt.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        client = kwargs.pop('client', None)
        super().__init__(*args, **kwargs)
        
        if client:
            self.fields['prompt'].queryset = AnalysisPrompt.objects.filter(client=client)