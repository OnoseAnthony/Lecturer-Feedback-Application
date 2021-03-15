from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from accounts.models import User
from reviews.models import (Answer, Question, Student, StudentAnswer,
                              Department, Level)


class InstructorSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_instructor = True
        if commit:
            user.save()
        return user

class StudentSignUpForm(UserCreationForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        widget=forms.Select,
        required=True
    )

    level = forms.ModelChoiceField(
        queryset=Level.objects.all(),
        widget=forms.Select,
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User


    def __init__(self, *args, **kwargs):
        super(StudentSignUpForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.save()
        student = Student.objects.create(user=user)
        student.department.add(self.cleaned_data.get('department'))
        student.level.add(self.cleaned_data.get('level'))
        return user

class StudentDepartmentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('department',)
        widgets = {
            'department': forms.Select
        }

class StudentLevelForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('level',)
        widgets = {
            'level': forms.Select
        }


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name',
            'username', 'is_student', 'is_instructor',
             )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password1 = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name',
            'username', 'is_student', 'is_instructor',
             )

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password1"]
