from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('update_task/<int:task_id>/', views.update_task, name='update_task'),
]
