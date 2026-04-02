import pandas as pd
import os
from decimal import Decimal
from django.utils.timezone import now
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User , Group
from django.contrib.auth.views import LoginView, LogoutView
from django.core.files import File
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.db.models import Avg,Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from io import BytesIO
from django.views.generic import DetailView, FormView, ListView, TemplateView
from .forms import BugForm, BugStatusUploadForm,UserProfileForm,UserForm,CustomRegisterForm,SprintForm
from .models import Bug,UserProfile,Sprint
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import DeveloperBugStatsSerializer, BugSerializer

class DeveloperBugStatsView(APIView):
    def get(self, request):
        try:
            developer_group = Group.objects.get(name='Developer')
            tester_group = Group.objects.get(name='Tester')
        except Group.DoesNotExist:
            return Response({"error": "Developer group not found"}, status=404)

        developers = User.objects.filter(groups__in=[developer_group, tester_group]).distinct()

        data = []
        for dev in developers:
            bugs = Bug.objects.filter(fixed_by__username=dev)
            bug_cr = Bug.objects.filter(created_by__username=dev)
            data.append({
                'developer': dev,
                'bugs_completed': bugs.filter(status='Fixed').count()+bugs.filter(status='Closed').count(),
                'bugs_created':bug_cr.count(),
            })

        serializer = DeveloperBugStatsSerializer(data, many=True)
        return Response(serializer.data)

class BugDurationAPIView(APIView):
    def get(self, request):
        bugs = Bug.objects.all()
        data = []
        for bug in bugs:
            duration = bug.updated_at - bug.created_at
            data.append({
                'id': bug.id,
                'title': bug.title,
                'status': bug.status,
                'duration': str(duration),
            })
        return Response(data)


@login_required
def fix_bug(request, pk):
    bug = get_object_or_404(Bug, pk=pk)

    # Check that:
    # 1. The user is not the creator
    # 2. The bug is not already fixed
    # 3. The user is in the sprint's developers
    if (
        bug.created_by != request.user and
        bug.fixed_by is None and
        bug.sprint and  
        request.user in bug.sprint.developers.all()
    ):
        bug.fixed_by = request.user
        bug.status = "Fixed"

        time_diff = now() - bug.created_at
        hours = Decimal(time_diff.total_seconds() / 3600)
        bug.time_spent_hours = round(hours, 2)

        bug.save()
        messages.success(request, "Bug marked as fixed.")
    else:
        messages.warning(request, "You are not authorized to fix this bug.")

    return redirect('django_bugapp:bug-detail', pk=pk)


class BugCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'django_bugapp/bug_form.html'

    def get(self, request, *args, **kwargs):
        form = BugForm()
        return self.render_to_response({'form': form})

    def post(self, request, *args, **kwargs):
        form = BugForm(request.POST, request.FILES)
        if form.is_valid():
            bug = form.save(commit=False)
            bug.created_by = request.user
            bug.save()
            return redirect('django_bugapp:bug-list')
        return self.render_to_response({'form': form})

class BugEditView(LoginRequiredMixin, TemplateView):
    template_name = 'django_bugapp/bug_form.html'

    def get_object(self):
        return Bug.objects.get(pk=self.kwargs['pk'], created_by=self.request.user)

    def get(self, request, *args, **kwargs):
        bug = self.get_object()
        form = BugForm(instance=bug)
        return self.render_to_response({'form': form, 'edit': True})

    def post(self, request, *args, **kwargs):
        bug = self.get_object()
        form = BugForm(request.POST, request.FILES, instance=bug)
        if form.is_valid():
            form.save()
            return redirect('django_bugapp:bug-detail', pk=bug.pk)
        return self.render_to_response({'form': form, 'edit': True})



# Home view
def home(request):
    return render(request, 'base.html')  # Create this template

def reports(request):
    return render(request, 'django_bugapp/bug_reports.html')  # Create this template

# Login view
class CustomLoginView(LoginView):
    template_name = 'django_bugapp/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('django_bugapp:home')

# Logout views
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('django_bugapp:login')

# Register view
class RegisterView(FormView):
    template_name = 'django_bugapp/register.html'
    form_class = CustomRegisterForm
    success_url = reverse_lazy('django_bugapp:home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_superuser:
            return redirect('django_bugapp:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        role = form.cleaned_data.get('role')
        group = Group.objects.get(name=role)
        user.groups.add(group)
        UserProfile.objects.create(user=user)
        login(self.request, user)
        return super().form_valid(form)

# Bug list (visible only to logged-in users)
class BugListView(LoginRequiredMixin, ListView):
    model = Bug
    template_name = 'django_bugapp/bug_list.html'
    context_object_name = 'bugs'
    login_url = reverse_lazy('django_bugapp:login')
    

# Bug detail (visible only to logged-in users)

class BugDetailView(LoginRequiredMixin, DetailView):
    model = Bug
    template_name = 'django_bugapp/bug_detail.html'
    context_object_name = 'bug'
    login_url = reverse_lazy('django_bugapp:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bug = self.get_object()
        user = self.request.user

        # Add 'can_fix' to context
        can_fix = (
            user.is_authenticated and
            bug.created_by != user and
            bug.fixed_by is None and
            bug.sprint and
            user in bug.sprint.developers.all()
        )

        context['can_fix'] = can_fix
        return context
    

def bugreport(request):
    
    if request.GET.get('download') == 'true':
        # Handle Excel download
        bugs = Bug.objects.all().values(
        'bug_id', 'title', 'info', 'status',
        'created_by__username', 'fixed_by__username',
        'created_at', 'updated_at',
        'screenshot' ,'sprint' ,'time_spent_hours' 
        )
        df = pd.DataFrame(list(bugs))

        for col in ['created_at', 'updated_at']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.tz_localize(None)
        
        df.rename(columns={
        'created_by__username': 'Created By',
        'fixed_by__username': 'Fixed By',
        'created_at': 'Created At',
        'updated_at': 'Fixed At',
        'contact_number': 'Contact Number',
        'info': 'Description',
        'bug_id': 'Bug ID'
    }, inplace=True)

        #df.to_excel('bug_report.xlsx', index=False)
        #return render(request, 'django_bugapp/bug_reports.html')
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Bugs')

        buffer.seek(0)


        response = HttpResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        response['Content-Disposition'] = 'attachment; filename="bug_report.xlsx"'
        return response



    if request.method == 'POST':
        # Handle Excel upload
        form = BugStatusUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                df = pd.read_excel(file)

                for _, row in df.iterrows():
                    bug_id = str(row.get('bug_id')).strip() if row.get('bug_id') else None
                    new_status = str(row.get('status')).strip() if row.get('status') else None
                    print(bug_id)
                    print(new_status)
                    if pd.notna(bug_id) and pd.notna(new_status):
                        try:
                            bug = Bug.objects.get(bug_id=bug_id)
                            bug.status = new_status
                            bug.title = row.get('title', bug.title)
                            bug.info = row.get('Description', bug.info)
                            bug.contact_number = row.get('Contact Number', bug.contact_number)
                            bug.created_by = User.objects.filter(username=row.get('Created By')).first()
                            bug.fixed_by = User.objects.filter(username=row.get('Fixed By')).first()
                            screenshot = row.get('screenshot')
                            bug.sprint = row.get('sprint')
                            bug.time_spent_hours = row.get('time_spent_hours')
                            if pd.notna(screenshot):
                                full_path = os.path.join('media', screenshot)

                                if os.path.exists(full_path):
                                    with open(full_path, 'rb') as f:
                                        bug.screenshot.save(os.path.basename(full_path), File(f), save=False)

                            bug.save()
                        except Bug.DoesNotExist:
                              bug=Bug.objects.create(
                                bug_id=bug_id,
                                title=row.get('title', ''),
                                info=row.get('Description', ''),
                                status = str(row.get('status')).strip() if row.get('status') else None,
                                contact_number=row.get('Contact Number', ''),
                                created_by = User.objects.filter(username=row.get('Created By')).first(),
                                fixed_by = User.objects.filter(username=row.get('Fixed By')).first(),
                                )
                              screenshot = row.get('screenshot','')  
                              if pd.notna(screenshot):
                                full_path = os.path.join('media', screenshot)
                                print(full_path)
                                if os.path.exists(full_path):
                                    with open(full_path, 'rb') as f:
                                        bug.screenshot.save(os.path.basename(full_path), File(f), save=False)
                              bug.save()  
                messages.success(request, "Bug statuses updated successfully.")
                return redirect('django_bugapp:bug_reports')
            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
        else:
            messages.error(request, "Invalid file upload. Only .xlsx files are supported.")
    else:
        form = BugStatusUploadForm()

    return render(request, 'django_bugapp/bug_reports.html', {'form': form})

@login_required
@permission_required('django_bugapp.edit_user_profile_perm')
def edit_profile(request):
    user = request.user
    UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST,instance=user)
        profile_form = UserProfileForm(request.POST,instance=user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('django_bugapp:profile')
    else:
        user_form = UserForm(instance=user) 
        profile_form = UserProfileForm(instance=user.userprofile)

        return render(request,'edit_profile.html',
                      {
                          'user_form':user_form,
                          'profile_form':profile_form,
                      }
) 

@login_required
def profile_view(request):
    user = request.user
    bugs_created = Bug.objects.filter(created_by=user).count()
    bugs_fixed = Bug.objects.filter(fixed_by=user).count()
    
    return render(request, 'profile.html', {
        'user': user,
        'bugs_created': bugs_created,
        'bugs_fixed': bugs_fixed,
    })


@login_required
def sprint_detail_view(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id)
    bugs = sprint.bugs.all() 
    total_sprint_time = bugs.aggregate(total=Sum('time_spent_hours'))['total'] or 0
    platform_avg = bugs.values('platform').annotate(avg_time=Avg('time_spent_hours'))
    developers = sprint.developers.all()
    developer_avg = []
    developer_total = []
    for dev in developers:
        dev_bugs = bugs.filter(fixed_by=dev)
        dev_avg = dev_bugs.aggregate(avg_time=Avg('time_spent_hours'))['avg_time'] or 0
        dev_total = dev_bugs.aggregate(total_time=Sum('time_spent_hours'))['total_time'] or 0
        developer_avg.append({'username': dev.username, 'avg_time': dev_avg})
        developer_total.append({'username': dev.username, 'total_time': dev_total})

    context = {
        'sprint': sprint,
        'bugs': bugs,
        'total_sprint_time': total_sprint_time,
        'platform_avg': platform_avg,
        'developer_avg': developer_avg,
        'developer_total': developer_total,
        'total_sprint_time':bugs.aggregate(total_time=Sum('time_spent_hours'))['total_time'] or 0
    }
    return render(request, 'sprints/sprint_detail.html', context)

@login_required
def sprint_list_view(request):
    sprint_list = Sprint.objects.all().order_by('id')  
    paginator = Paginator(sprint_list, 1) 

    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'sprints/sprint_list.html', {
        'page_obj': page_obj,
        'sprints': page_obj.object_list 
    })


@login_required
def sprint_create_view(request):
    if request.method == 'POST':
        form = SprintForm(request.POST)
        if form.is_valid():
            # Save the Sprint instance first to generate an ID
            sprint = form.save()

            # Now that the Sprint instance has an ID, we can assign developers
            developers = form.cleaned_data['developers']
            sprint.developers.set(developers)

            # Save the Sprint instance with the developers assigned
            sprint.save()

            return redirect('django_bugapp:sprint_list')
    else:
        form = SprintForm()

    return render(request, 'sprints/sprint_form.html', {'form': form})

@login_required
def sprint_edit_view(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id)
    if request.method == 'POST':
        form = SprintForm(request.POST, instance=sprint)
        if form.is_valid():
            form.save()
            return redirect('django_bugapp:sprint_detail', sprint_id=sprint.id)
    else:
        form = SprintForm(instance=sprint)
    return render(request, 'sprints/sprint_form.html', {'form': form})

@login_required
def userlistview(request):
    users = User.objects.annotate(
        avg_time_spent=Avg('fixed_bugs__time_spent_hours')
    )
    return render(request,'django_bugapp/user_list.html',{"users":users})
    