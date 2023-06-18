from django.urls import path
from . import views

urlpatterns = [
    path("mine/", views.ManageProjectListView.as_view(), name="manage_project_list"),
    path("create/", views.ProjectCreateView.as_view(), name="project_create"),
    path("<pk>/edit/", views.ProjectUpdateView.as_view(), name="project_edit"),
    path("<pk>/delete/", views.ProjectDeleteView.as_view(), name="project_delete"),
    path("<pk>/module/", views.ProjectModuleUpdateView.as_view(),       name="project_module_update"),
    path('content/<int:content_id>/project/<model_name>/create/', views.ContentsCreateUpdateView.as_view(), name='module_content_create'),
    path('content/<int:content_id>/project/<model_name>/<id>/', views.ContentsCreateUpdateView.as_view(), name='module_content_update'),
    path('content/<int:id>/delete/', views.ContentsDeleteView.as_view(), name='module_content_delete'),
    path('content/<int:content_id>/', views.ContentContentsListView.as_view(), name='module_content_list'),
]
