from django.contrib import admin
from reviews.models import Answer, Assessment, Question, Student, StudentAnswer, TakenAssessment

# Register your models here.



admin.site.register(Student)
admin.site.register(Answer)
admin.site.register(Assessment)
admin.site.register(Question)
admin.site.register(StudentAnswer)
admin.site.register(TakenAssessment)
