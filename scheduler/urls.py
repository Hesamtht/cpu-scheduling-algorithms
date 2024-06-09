from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_processes/', views.get_processes, name='get_processes'),
    path('add_process/', views.add_process, name='add_process'),
    path('delete_process/<int:process_id>/', views.delete_process, name='delete_process'),
    path('schedule/', views.schedule, name='schedule'),
    path('mlfq/', views.mlfq_view, name='mlfq'),
    path('mlfq_get_processes/', views.mlfq_get_processes, name='mlfq_get_processes'),
    path('mlfq_add_process/', views.mlfq_add_process, name='mlfq_add_process'),
    path('mlfq_schedule/', views.mlfq_schedule, name='mlfq_schedule'),
    path('elevator/', views.elevator_view, name='elevator'),
    path('run_elevator/', views.run_elevator, name='run_elevator'),
    path('round_robin/', views.round_robin, name='round_robin'),
    path('round_robin_schedule/', views.round_robin_schedule, name='round_robin_schedule'),
    path('banker/', views.banker_view, name='banker'),
    path('run_banker/', views.run_banker, name='run_banker'),
]
