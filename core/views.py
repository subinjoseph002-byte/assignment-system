from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from core.forms import CustomUserCreationForm, AssignmentForm, SubmissionForm, MarkForm
from core.models import User, Assignment, Submission, Mark, Notification
from django.contrib.auth.decorators import login_required
from core.decorators import role_required

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('login')

@login_required
def dashboard_view(request):
    role = request.user.role
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'teacher':
        return redirect('teacher_dashboard')
    else:
        return redirect('student_dashboard')

@login_required
@role_required('admin')
def admin_dashboard(request):
    users = User.objects.all().order_by('-date_joined')
    context = {
        'total_teachers': User.objects.filter(role='teacher').count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_assignments': Assignment.objects.count(),
        'total_submissions': Submission.objects.count(),
        'recent_assignments': Assignment.objects.order_by('-created_at')[:5],
        'users': users
    }
    return render(request, 'dashboards/admin.html', context)

@login_required
@role_required('teacher')
def teacher_dashboard(request):
    assignments = Assignment.objects.filter(created_by=request.user).order_by('-deadline')
    return render(request, 'dashboards/teacher.html', {'assignments': assignments})

@login_required
@role_required('student')
def student_dashboard(request):
    
    # Simple logic: all assignments system-wide for prototype, or we could filter by subject
    assignments = Assignment.objects.all().order_by('deadline')
    return render(request, 'dashboards/student.html', {'assignments': assignments})

@login_required
@role_required('teacher')
def assignment_create(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            
            # Notify all students
            students = User.objects.filter(role='student')
            notifications = [
                Notification(user=student, message=f"New assignment: {assignment.title}")
                for student in students
            ]
            Notification.objects.bulk_create(notifications)
            
            return redirect('teacher_dashboard')
    else:
        form = AssignmentForm()
    return render(request, 'assignments/create.html', {'form': form})

@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    
    if request.user.role == 'student':
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
        if request.method == 'POST':
            if not submission:
                form = SubmissionForm(request.POST, request.FILES)
                if form.is_valid():
                    sub = form.save(commit=False)
                    sub.assignment = assignment
                    sub.student = request.user
                    sub.save()
                    return redirect('assignment_detail', pk=assignment.id)
            else:
                form = None
        else:
            form = SubmissionForm() if not submission else None
            
        return render(request, 'assignments/detail_student.html', {
            'assignment': assignment,
            'submission': submission,
            'form': form
        })
        
    elif request.user.role in ['teacher', 'admin']:
        submissions = assignment.submissions.all()
        return render(request, 'assignments/detail_teacher.html', {
            'assignment': assignment,
            'submissions': submissions
        })
    else:
        return redirect('dashboard')
        
@login_required
@role_required('teacher')
def evaluate_submission(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    mark = getattr(submission, 'mark', None)
    
    if request.method == 'POST':
        form = MarkForm(request.POST, instance=mark)
        if form.is_valid():
            m = form.save(commit=False)
            m.submission = submission
            m.save()
            
            # Notify the student
            Notification.objects.create(
                user=submission.student,
                message=f"Your assignment '{submission.assignment.title}' was graded!"
            )
            
            return redirect('assignment_detail', pk=submission.assignment.id)
    else:
        form = MarkForm(instance=mark)
        
    return render(request, 'assignments/evaluate.html', {
        'submission': submission,
        'form': form
    })

@login_required
@role_required('teacher')
def assignment_update(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            form.save()
            # Notify students about the update
            students = User.objects.filter(role='student')
            notifications = [
                Notification(user=student, message=f"Assignment updated: {assignment.title}")
                for student in students
            ]
            Notification.objects.bulk_create(notifications)
            return redirect('teacher_dashboard')
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, 'assignments/update.html', {'form': form, 'assignment': assignment})

@login_required
@role_required('teacher')
def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    if request.method == 'POST':
        assignment.delete()
        return redirect('teacher_dashboard')
    return render(request, 'assignments/delete.html', {'assignment': assignment})

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
@role_required('admin')
def change_user_role(request, user_id):
    if request.method == 'POST':
        user_to_change = get_object_or_404(User, id=user_id)
        new_role = request.POST.get('role')
        if new_role in ['admin', 'teacher', 'student']:
            user_to_change.role = new_role
            # Also ensure staff status for admins
            user_to_change.is_staff = (new_role == 'admin')
            user_to_change.save()
    return redirect('admin_dashboard')

@login_required
@role_required('admin')
def delete_user(request, user_id):
    if request.method == 'POST':
        user_to_delete = get_object_or_404(User, id=user_id)
        if user_to_delete != request.user:
            user_to_delete.delete()
    return redirect('admin_dashboard')
