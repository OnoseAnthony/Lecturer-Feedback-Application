import time
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, TemplateView
from django.contrib import messages

from accounts.decorators import student_required, instructor_required
from accounts.forms import StudentLevelForm, StudentSignUpForm, StudentDepartmentForm, InstructorSignUpForm
from accounts.models import User
from reviews.models import Student

# Create your views here.

@login_required
def change_password(request):
    content = ''
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('home')
        else:
            messages.error(request, 'Please check form fields.', extra_tags = 'echangepwd')
            return redirect('/accounts/profile/change-password')
    else:
        form = PasswordChangeForm(user=request.user)

    for field in form.fields.values():
        field.help_text = None

    args = {'form': form,}
    return render(request, 'accounts/change_password.html', args)


def user_login(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            # correct username and password login the user
            login(request, user)
            return HttpResponseRedirect(reverse('home'))
        else:
            context['error'] = "Provide Valid Credentials !!"
            return render(request, 'accounts/login.html', context)

    else:
        return render(request, 'accounts/login.html', context)


@login_required
def user_logout(request):
        logout(request)
        return HttpResponseRedirect(reverse('home'))



class RegisterView(TemplateView):
    template_name = 'accounts/register.html'



class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'accounts/reg_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('reviews:students:assessment_list')


    def form_invalid(self, form):
        messages.error(self.request, 'Please check form fields.', extra_tags = 'esignup')
        return redirect('accounts:student_signup')




class InstructorSignUpView(CreateView):
    model = User
    form_class = InstructorSignUpForm
    template_name = 'accounts/reg_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'instructor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('reviews:instructors:assessment_change_list')
