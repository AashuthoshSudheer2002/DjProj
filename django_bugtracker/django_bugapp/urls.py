from django.urls import path
from .views import (
    BugListView, BugDetailView,
    CustomLoginView, CustomLogoutView, RegisterView, BugCreateView, BugEditView ,BugDurationAPIView,DeveloperBugStatsView,
    home , userlistview, fix_bug , bugreport , profile_view, edit_profile,sprint_create_view,sprint_detail_view,sprint_edit_view,sprint_list_view
)
from django.contrib.auth.views import PasswordChangeView,PasswordChangeDoneView


app_name = 'django_bugapp'

urlpatterns = [
    path('', home, name='home'),
    path('reports/',bugreport , name='bug_reports'),
    path('bugs/', BugListView.as_view(), name='bug-list'),
    path('bugs/<int:pk>/', BugDetailView.as_view(), name='bug-detail'),
    path('bugs/new/', BugCreateView.as_view(), name='bug-create'),
    path('bugs/<int:pk>/edit/', BugEditView.as_view(), name='bug-edit'),
    path('bugs/<int:pk>/fix/', fix_bug, name='bug-fix'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', profile_view,name='profile'),
    path('profile/edit/', edit_profile,name='edit_profile'),
    path('profile/password/',PasswordChangeView.as_view(template_name='change_password.html'),name='change_password'),
    path('profile/password/done/',PasswordChangeDoneView.as_view(template_name='change_password_done.html'), name='password_change_done'),
    path('api/developer-bug-stats/', DeveloperBugStatsView.as_view(), name='developer-bug-stats'),
    path('api/bug-durations/', BugDurationAPIView.as_view(), name='bug-durations'),
    path('sprints/', sprint_list_view, name='sprint_list'),
    path('sprints/create/', sprint_create_view, name='sprint_create'),
    path('sprints/<int:sprint_id>/', sprint_detail_view, name='sprint_detail'),
    path('sprints/<int:sprint_id>/edit/', sprint_edit_view, name='sprint_edit'),
    path('users/', userlistview, name='user-list'),
]
