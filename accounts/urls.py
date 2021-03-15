from django.urls import path, include
from accounts import views





#Template Tagging
app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login, name='user_login'),
    path('register/', views.RegisterView.as_view(), name='signup'),
    path('register/student', views.StudentSignUpView.as_view(), name='student_signup'),
    path('register/instructor', views.InstructorSignUpView.as_view(), name='instructor_signup'),
    path('profile/logout/', views.user_logout, name='user_logout'),
    path('profile/change-password/', views.change_password, name='change_password')
]
