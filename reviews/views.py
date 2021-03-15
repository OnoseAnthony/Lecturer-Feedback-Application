from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.conf import settings
from django.db.models import Avg, Count
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DetailView, ListView, UpdateView, TemplateView,
                                    DeleteView)

from accounts.decorators import student_required, instructor_required
from reviews.forms import BaseAnswerInlineFormSet, QuestionForm, TakeAssessmentForm
from accounts.forms import StudentLevelForm, StudentSignUpForm, StudentDepartmentForm, InstructorSignUpForm
from accounts.models import User
from reviews.models import Student, Assessment, TakenAssessment, Question, Answer

import paralleldots
from textblob import TextBlob

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import time

# Create your views here.


style.use("ggplot")
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)


poscount = 0
negcount = 0
neutralcount = 0

def analyse1(wiki):
    global poscount
    global negcount
    global neutralcount
    user_response = TextBlob(wiki)
    if (user_response.sentiment.polarity == 0.0):
        fname=  "Your remark is Neutral"
        print(fname)
        neutralcount +=1
    elif (user_response.sentiment.polarity > 0.0 and user_response.sentiment.polarity <= 1.0):
        fname = "Your remark is Positive"
        print(fname)
        poscount +=1
    else:
        fname="Your remark is Negative"
        print(fname)
        negcount +=1



@method_decorator([login_required, student_required], name='dispatch')
class StudentDepartmentView(UpdateView):
    model = Student
    form_class = StudentDepartmentForm
    template_name = 'reviews/students/department_form.html'
    success_url = reverse_lazy('reviews:students:assessment_list')

    def get_object(self):
        return self.request.user.student

    def form_valid(self, form):
        return super().form_valid(form)


@method_decorator([login_required, student_required], name='dispatch')
class StudentLevelView(UpdateView):
    model = Student
    form_class = StudentLevelForm
    template_name = 'reviews/students/level_form.html'
    success_url = reverse_lazy('reviews:students:assessment_list')

    def get_object(self):
        return self.request.user.student

    def form_valid(self, form):
        return super().form_valid(form)


@method_decorator([login_required, student_required], name='dispatch')
class AssessmentListView(ListView):
    model = Assessment
    ordering = ('name', )
    context_object_name = 'assessments'
    template_name = 'reviews/students/assessment_list.html'

    def get_queryset(self):
        student = self.request.user.student
        student_department = student.department.values_list('pk', flat=True)
        student_level = student.level.values_list('pk', flat=True)
        taken_assessments = student.assessments.values_list('pk', flat=True)
        queryset = Assessment.objects.filter(department__in=student_department, level__in=student_level) \
            .exclude(pk__in=taken_assessments) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset


@method_decorator([login_required, student_required], name='dispatch')
class TakenAssessmentListView(ListView):
    model = TakenAssessment
    context_object_name = 'taken_assessments'
    template_name = 'reviews/students/taken_assessment_list.html'

    def get_queryset(self):
        queryset = self.request.user.student.taken_assessments \
            .select_related('assessment', 'assessment__department', 'assessment__level') \
            .order_by('assessment__name')
        return queryset



@login_required
@student_required
def take_assessment(request, pk):
    global poscount
    global negcount
    global neutralcount
    fname = ""
    fnamevalue = 0
    assessment = get_object_or_404(Assessment, pk=pk)
    student = request.user.student

    if student.assessments.filter(pk=pk).exists():
        return render(request, 'reviews/students/taken_assessment_list.html')

    total_questions = assessment.questions.count()
    unanswered_questions = student.get_unanswered_questions(assessment)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeAssessmentForm(question=question, data=request.POST)
        if form.is_valid():
            if form.cleaned_data['answer']:
                sent = form.cleaned_data['answer']
                sent1 = str(sent)
                print(sent1)
                user_response = analyse1(sent1)
                if (poscount > negcount and poscount > neutralcount):
                    fname=  "Excellent"
                elif (negcount > poscount and negcount > neutralcount):
                    fname = "Negative"
                else:
                    fname = "Neutral"
                if (fname == "Excellent"):
                    fnamevalue = 1
                elif(fname == "Negative"):
                    fnamevalue = -1
                else:
                    fnamevalue = 0
                with transaction.atomic():
                    student_answer = form.save(commit=False)
                    student_answer.student = student
                    student_answer.save()
                    assessment.remark = fname
                    assessment.rating = fnamevalue
                    assessment.save()
                    if student.get_unanswered_questions(assessment).exists():
                        return redirect('reviews:students:take_assessment', pk)
                    else:
                        TakenAssessment.objects.create(student=student, assessment=assessment, remark= fname, rating=fnamevalue)
                        return redirect('reviews:students:assessment_list')
            else:
                sent = form.cleaned_data['comment']
                sent1 = str(sent)
                print(sent1)
                user_response = analyse1(sent1)
                if (poscount > negcount and poscount > neutralcount):
                    fname=  "Excellent"
                elif (negcount > poscount and negcount > neutralcount):
                    fname = "Negative"
                else:
                    fname = "Neutral"
                if (fname == "Excellent"):
                    fnamevalue = 1
                elif(fname == "Negative"):
                    fnamevalue = -1
                else:
                    fnamevalue = 0
                with transaction.atomic():
                    Adt = Answer.objects.create(question=question, text=sent)
                    student_answer = form.save(commit=False)
                    student_answer.student = student
                    student_answer.save()
                    assessment.remark = fname
                    assessment.rating = fnamevalue
                    assessment.save()
                    if student.get_unanswered_questions(assessment).exists():
                        return redirect('reviews:students:take_assessment', pk)
                    else:
                        TakenAssessment.objects.create(student=student, assessment=assessment, remark= fname, rating=fnamevalue)
                        return redirect('reviews:students:assessment_list')
    else:
        form = TakeAssessmentForm(question=question)

    return render(request, 'reviews/students/take_assessment_form.html', {
        'assessment': assessment,
        'question': question,
        'form': form,
        'progress': progress
    })


@method_decorator([login_required, instructor_required], name='dispatch')
class DassessmentListView(ListView):
    model = Assessment
    ordering = ('name', )
    context_object_name = 'assessments'
    template_name = 'reviews/instructors/assessment_change_list.html'


    def get_context_data(self, **kwargs):
        fnamez = ""
        r = ""
        r1 = ""
        r2 = ""
        r3 = ""
        r4 = ""
        counterz = 0
        pcountz = 0
        negcountz = 0
        ncountz = 0
        emailmessage = ""
        x = 0
        y = 0
        xar = []
        yar = []
        assessment = self.request.user.assessments.all()
        print(assessment)


        for assessments in assessment:
            print(assessments.remark)
            x += 1
            counterz += 1

            if (assessments.rating == -1):
                y -= 0.2
                negcountz +=1
            elif (assessments.rating == 0):
                ncountz +=1
            elif (assessments.rating == 1):
                pcountz +=1
                y += 1
            else:
                print("It's possible the assessment hasn't be taken yet by any student yet")


            xar.append(x)
            yar.append(y)

            ax1.clear()
            ax1.plot(xar,yar)
            fig.savefig(settings.STATIC_DIR + '/media/my_plot.png')

        if (pcountz > negcountz and pcountz > ncountz):
            fnamez =  "Excellent"
            r = "From the analysed graph, we observe that you have been reviewed excellently well. However, there are a few recommendations we would like to suggest to help you serve better:"
            r1 = "Positive recommendation"
            r2 = "Positive recommendation"
            r3 = "Positive recommendation"
            r4 = "Positive recommendation"

        elif (negcountz > pcountz and negcountz > ncountz):
            fnamez = " Negative"
            r = "From the analysed graph, we observe that you have been reviewed poorly. Here are a few recommendations and adjustment we would like to suggest to help you serve better:"
            r1 = "Negative recommendation"
            r2 = "Negative recommendation"
            r3 = "Negative recommendation"
            r4 = "Negative recommendation"

        else:
            fnamez = "Neutral"
            r = "From the analysed graph, we observe that your review sits in between positive and negative and as such it has a neutral standing. However, there are a few recommendations and adjustment we would like to suggest to help you serve better:"
            r1 = "Neutral recommendation"
            r2 = "Neutral recommendation"
            r3 = "Neutral recommendation"
            r4 = "Neutral recommendation"


        extra_context = {
                'newst': counterz,
                'pos': pcountz,
                'neg': negcountz,
                'neu': ncountz,
                'fname': fnamez,
                'r': r,
                'r1': r1,
                'r2': r2,
                'r3': r3,
                'r4': r4

        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = self.request.user.assessments \
            .select_related('department', 'level') \
            .annotate(questions_count=Count('questions', distinct=True)) \
            .annotate(taken_count=Count('taken_assessments', distinct=True))
        return queryset


@method_decorator([login_required, instructor_required], name='dispatch')
class AssessmentCreateView(CreateView):
    model = Assessment
    fields = ('name', 'department', 'level', )
    template_name = 'reviews/instructors/assessment_add_form.html'

    def form_valid(self, form):
        assessment = form.save(commit=False)
        assessment.owner = self.request.user

        if assessment.department == self.request.user.department:
            assessment.save()
            messages.success(self.request, 'The Assessment was created with success! Go ahead and add some questions now.', extra_tags= 'screateassess')
            return redirect('reviews:instructors:assessment_change', assessment.pk)
        else:
            messages.error(self.request, 'Lecturer can only create assessments for students in his department.', extra_tags = 'ecreateassess')
            return redirect('reviews:instructors:assessment_add')




@method_decorator([login_required, instructor_required], name='dispatch')
class AssessmentUpdateView(UpdateView):
    model = Assessment
    fields = ('name', 'level',)
    context_object_name = 'assessment'
    template_name = 'reviews/instructors/assessment_change_form.html'



    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing quizzes that belongs
        to the logged in user.
        '''
        return self.request.user.assessments.all()

    def get_success_url(self):
        return reverse('reviews:instructors:assessment_change', kwargs={'pk': self.object.pk})



@method_decorator([login_required, instructor_required], name='dispatch')
class AssessmentDeleteView(DeleteView):
    model = Assessment
    context_object_name = 'assessment'
    template_name = 'reviews/instructors/assessment_delete_confirm.html'
    success_url = reverse_lazy('reviews:instructors:assessment_change_list')

    def delete(self, request, *args, **kwargs):
        assessment = self.get_object()
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.assessments.all()


@method_decorator([login_required, instructor_required], name='dispatch')
class AssessmentResultsView(DetailView):
    model = Assessment
    context_object_name = 'assessment'
    template_name = 'reviews/instructors/assessment_results.html'

    def get_context_data(self, **kwargs):
        fnamezz = ""
        r5 = ""
        r6 = ""
        r7 = ""
        r8 = ""
        r9 = ""
        a = 0
        b = 0
        xarr = []
        yarr = []
        pcountzz = 0
        negcountzz = 0
        ncountzz = 0
        assessment = self.get_object()
        assess_remark = assessment.remark
        assess_rating = assessment.rating
        taken_assessments = assessment.taken_assessments.select_related('student__user').order_by('-date')
        take = TakenAssessment.objects.all()
        print(take)
        total_taken_assessments = taken_assessments.count()

        for taken_assessment in take:
            print(taken_assessment.remark)
            a += 1

            if (taken_assessment.rating == -1):
                b = 0.2
                negcountzz += 1

            elif (taken_assessment.rating == 0):
                ncountzz += 1

            elif (taken_assessment.rating == 1):
                pcountzz += 1
                b += 1

            else:
                print('wassup')

            xarr.append(a)
            yarr.append(b)

            ax1.clear()
            ax1.plot(xarr,yarr)
            fig.savefig(settings.STATIC_DIR + '/media/my_plot.png')

        if (pcountzz > negcountzz and pcountzz > ncountzz):
            fnamezz =  "Excellent"
            r5 = "From the analysed graph, we observe that you have been reviewed excellently well. However, there are a few recommendations we would like to suggest to help you serve better:"
            r6 = "Positive recommendation"
            r7 = "Positive recommendation"
            r8 = "Positive recommendation"
            r9 = "Positive recommendation"

        elif (negcountzz > pcountzz and negcountzz > ncountzz):
            fnamezz = " Negative"
            r5 = "From the analysed graph, we observe that you have been reviewed poorly. Here are a few recommendations and adjustment we would like to suggest to help you serve better:"
            r6 = "Negative recommendation"
            r7 = "Negative recommendation"
            r8 = "Negative recommendation"
            r9 = "Negative recommendation"

        else:
            fnamezz = "Neutral"
            r5 = "From the analysed graph, we observe that your review sits in between positive and negative and as such it has a neutral standing. However, there are a few recommendations and adjustment we would like to suggest to help you serve better:"
            r6 = "Neutral recommendation"
            r7 = "Neutral recommendation"
            r8 = "Neutral recommendation"
            r9 = "Neutral recommendation"

        extra_context = {
            'taken_assessments': taken_assessments,
            'total_taken_assessments': total_taken_assessments,
            'poss': pcountzz,
            'negg': negcountzz,
            'neuu': ncountzz,
            'fnamee': fnamezz,
            'r5': r5,
            'r6': r6,
            'r7': r7,
            'r8': r8,
            'r9': r9
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.assessments.all()




@login_required
@instructor_required
def question_add(request, pk):
    # By filtering the quiz by the url keyword argument `pk` and
    # by the owner, which is the logged in user, we are protecting
    # this view at the object-level. Meaning only the owner of
    # quiz will be able to add questions to it.
    assessment = get_object_or_404(Assessment, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.assessment = assessment
            question.save()
            return redirect('reviews:instructors:question_change', assessment.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'reviews/instructors/question_add_form.html', {'assessment': assessment, 'form': form})



@login_required
@instructor_required
def question_change(request, assessment_pk, question_pk):
    # Simlar to the `question_add` view, this view is also managing
    # the permissions at object-level. By querying both `quiz` and
    # `question` we are making sure only the owner of the quiz can
    # change its details and also only questions that belongs to this
    # specific quiz can be changed via this url (in cases where the
    # user might have forged/player with the url params.
    assessment = get_object_or_404(Assessment, pk=assessment_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, assessment=assessment)

    AnswerFormSet = inlineformset_factory(
        Question,  # parent model
        Answer,  # base model
        formset=BaseAnswerInlineFormSet,
        fields=('text',),
        min_num=0,
        validate_min=True,
        max_num=10,
        validate_max=True
    )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            return redirect('reviews:instructors:assessment_change', assessment.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

    return render(request, 'reviews/instructors/question_change_form.html', {
        'assessment': assessment,
        'question': question,
        'form': form,
        'formset': formset
    })


@method_decorator([login_required, instructor_required], name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'reviews/instructors/question_delete_confirm.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['assessment'] = question.assessment
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(assessment__owner=self.request.user)

    def get_success_url(self):
        question = self.get_object()
        return reverse('reviews:instructors:assessment_change', kwargs={'pk': question.assessment_id})
