from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('ramo/<int:ramo_id>/', views.ramo_detail, name='ramo_detail'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('add_course/', views.add_course, name='add_course'),
    path('edit_course/<int:ramo_id>/', views.edit_course, name='edit_course'),
    path('delete_course/<int:ramo_id>/', views.delete_course, name='delete_course'),
    path('save_grade/<int:evaluacion_id>/', views.save_grade, name='save_grade'),
    path('delete_evaluacion/<int:evaluacion_id>/', views.delete_evaluacion, name='delete_evaluacion'),
    path('save_nota_objetivo/<int:ramo_id>/', views.save_nota_objetivo, name='save_nota_objetivo'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
]
