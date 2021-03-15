from django.db import models
from django.utils.html import escape, mark_safe
from accounts.models import User, Department, Level

# Create your models here.



class Assessment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='assessments')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='assessments')
    remark  =   models.CharField(max_length=120, default="Excellent")
    rating  =   models.IntegerField(null=True, blank=True)
    def __str__(self):
        return self.name


class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=255)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Answer', max_length=255)

    def __str__(self):
        return self.text


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    assessments = models.ManyToManyField(Assessment, through='TakenAssessment')
    department = models.ManyToManyField(Department, related_name='interested_students')
    level = models.ManyToManyField(Level, related_name='interested_students')

    def get_unanswered_questions(self, assessment):
        answered_questions = self.assessment_answers \
            .filter(answer__question__assessment=assessment) \
            .values_list('answer__question__pk', flat=True)
        questions = assessment.questions.exclude(pk__in=answered_questions).order_by('text')
        return questions

    def __str__(self):
        return self.user.username

class TakenAssessment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='taken_assessments')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='taken_assessments')
    remark  =   models.CharField(max_length=120, default="Excellent")
    rating  =   models.IntegerField(null=True, blank=True)    
    date = models.DateTimeField(auto_now_add=True)


class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assessment_answers')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+' , null=True)
    comment = models.CharField(max_length=255, null=True)
