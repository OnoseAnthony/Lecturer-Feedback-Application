from django import forms
from django.db import transaction
from django.forms.utils import ValidationError

from accounts.models import User
from reviews.models import (Answer, Question, Student, StudentAnswer,
                              Department, Level)



class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text', )



class BaseAnswerInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                break



class TakeAssessmentForm(forms.ModelForm):
    answer = forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        widget=forms.RadioSelect(),
        required=False,
        empty_label=None)

    comment = forms.CharField(
        widget=forms.TextInput(),
        required=False,
        label = 'Comments')

    class Meta:
        model = StudentAnswer
        fields = ('answer', 'comment' )

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.answers.order_by('text')
