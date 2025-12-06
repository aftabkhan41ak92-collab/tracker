
from django.urls import path
from . import views

app_name = "tracker"

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),  #
    path('bmi/', views.bmi_calculator, name='bmi'),
    path('logout/', views.logout_view, name='logout'),
    path('history/', views.history, name='history'),
    path('record/<int:pk>/edit/', views.edit_record, name='edit_record'),
    path('record/<int:record_id>/delete/', views.delete_record, name='delete_record'),

]
