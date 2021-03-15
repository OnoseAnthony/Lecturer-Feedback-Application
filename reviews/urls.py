from django.urls import include, path

from reviews import views




#Template Tagging
app_name = 'reviews'


urlpatterns = [

    path('students/', include(([
        path('', views.AssessmentListView.as_view(), name='assessment_list'),
        path('department/', views.StudentDepartmentView.as_view(), name='student_department'),
        path('level/', views.StudentLevelView.as_view(), name='student_level'),
        path('taken/', views.TakenAssessmentListView.as_view(), name='taken_assessment_list'),
        path('assessment/<int:pk>/', views.take_assessment, name='take_assessment'),
    ], 'review'), namespace='students')),

    path('instructors/', include(([
        path('', views.DassessmentListView.as_view(), name='assessment_change_list'),
        path('assessment/add/', views.AssessmentCreateView.as_view(), name='assessment_add'),
        path('assessment/<int:pk>/', views.AssessmentUpdateView.as_view(), name='assessment_change'),
        path('assessment/<int:pk>/delete/', views.AssessmentDeleteView.as_view(), name='assessment_delete'),
        path('assessment/<int:pk>/results/', views.AssessmentResultsView.as_view(), name='assessment_results'),
        path('assessment/<int:pk>/question/add/', views.question_add, name='question_add'),
        path('assessment/<int:assessment_pk>/question/<int:question_pk>/', views.question_change, name='question_change'),
        path('assessment/<int:assessment_pk>/question/<int:question_pk>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),
    ], 'review'), namespace='instructors')),
]
