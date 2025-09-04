from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.ActivityCategoryListView.as_view(), name='activity-categories'),
    path('templates/', views.ActivityTemplateListView.as_view(), name='activity-templates'),
    path('', views.ActivityListCreateView.as_view(), name='activity-list-create'),
    path('<uuid:pk>/', views.ActivityDetailView.as_view(), name='activity-detail'),
    path('<uuid:activity_id>/recalculate/', views.recalculate_activity_co2, name='activity-recalculate'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]