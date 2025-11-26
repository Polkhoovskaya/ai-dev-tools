# ========================================
# FILE: todos/forms.py
# ========================================

from django import forms
from .models import Todo

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'due_date', 'is_resolved']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }
