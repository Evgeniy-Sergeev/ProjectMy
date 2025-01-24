from django import forms
from .models import Submission, Lesson


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['student', 'lesson', 'code']


class LessonSelectForm(forms.Form):
    lesson = forms.ModelChoiceField(queryset=Lesson.objects.all(), label="Select Lesson", empty_label=None)