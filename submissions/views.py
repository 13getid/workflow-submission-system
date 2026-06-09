from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.db.models import Q
from .forms import SubmissionForm
from .models import Submission


def home(request):
    return render(request, 'submissions/home.html')


def submit(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.save()
            messages.success(request, '🎉 Your submission was received successfully!')
            return redirect('dashboard')
    else:
        form = SubmissionForm()
    return render(request, 'submissions/submit.html', {'form': form})


def success(request):
    return render(request, 'submissions/success.html')


@login_required
def dashboard(request):
    submissions = Submission.objects.filter(
        user=request.user).order_by('-submitted_at')
    total = submissions.count()
    approved = submissions.filter(status='approved').count()
    pending = submissions.filter(status='pending').count()
    rejected = submissions.filter(status='rejected').count()
    context = {
        'submissions': submissions,
        'total': total,
        'approved': approved,
        'pending': pending,
        'rejected': rejected,
    }
    return render(request, 'submissions/dashboard.html', context)


@login_required
def edit_submission(request, submission_id):
    submission = Submission.objects.get(id=submission_id)

    # Only the owner can edit
    if submission.user != request.user:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Your submission was updated successfully!')
            return redirect('dashboard')
    else:
        form = SubmissionForm(instance=submission)

    return render(request, 'submissions/edit_submission.html', {
        'form': form,
        'submission': submission
    })
# ✅ edit_submission ends here — at zero indentation


@login_required
def delete_submission(request, submission_id):
    submission = Submission.objects.get(id=submission_id)

    # Only the owner can delete
    if submission.user != request.user:
        return redirect('dashboard')

    if request.method == 'POST':
        submission.delete()
        messages.success(request, '🗑️ Your submission was deleted.')
        return redirect('dashboard')

    return render(request, 'submissions/delete_submission.html', {
        'submission': submission
    })
# ✅ delete_submission ends here — at zero indentation


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('dashboard')
        else:
            return render(request, 'submissions/login.html', {'error': True})
    return render(request, 'submissions/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'submissions/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        return redirect('dashboard')

    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()

    total = Submission.objects.count()
    approved = Submission.objects.filter(status='approved').count()
    pending = Submission.objects.filter(status='pending').count()
    rejected = Submission.objects.filter(status='rejected').count()

    qs = Submission.objects.all().order_by('-submitted_at')

    if search:
        qs = qs.filter(
            Q(project_title__icontains=search) |
            Q(user__username__icontains=search)
        )

    if status_filter in ['pending', 'approved', 'rejected']:
        qs = qs.filter(status=status_filter)

    context = {
        'submissions': qs,
        'total': total,
        'approved': approved,
        'pending': pending,
        'rejected': rejected,
        'search': search,
        'status_filter': status_filter,
    }
    return render(request, 'submissions/admin_dashboard.html', context)


@login_required
def update_status(request, submission_id):
    if not is_admin(request.user):
        return redirect('dashboard')
    if request.method == 'POST':
        submission = Submission.objects.get(id=submission_id)
        old_status = submission.status
        new_status = request.POST['status']
        submission.status = new_status
        submission.save()
        if old_status != new_status:
            send_status_email(submission)
    return redirect('admin_dashboard')


def send_status_email(submission):
    username = submission.user.username
    email = submission.email
    project = submission.project_title
    status = submission.status

    if status == 'approved':
        subject = 'Your submission has been approved!'
        message = (
            'Hi ' + username + ',\n\n'
            'Great news! Your project submission has been reviewed and approved.\n\n'
            'Project: ' + project + '\n'
            'Status: Approved\n\n'
            'Log in to your dashboard to view the full details:\n'
            'http://127.0.0.1:8000/dashboard/\n\n'
            'Best regards,\n'
            'SwahiliPot Submission Team'
        )
    elif status == 'rejected':
        subject = 'Update on your submission'
        message = (
            'Hi ' + username + ',\n\n'
            'Thank you for your submission. After careful review, '
            'we regret to inform you that your project was not approved at this time.\n\n'
            'Project: ' + project + '\n'
            'Status: Rejected\n\n'
            'You are welcome to make improvements and submit again.\n\n'
            'Log in to your dashboard:\n'
            'http://127.0.0.1:8000/dashboard/\n\n'
            'Best regards,\n'
            'SwahiliPot Submission Team'
        )
    else:
        return

    send_mail(
        subject=subject,
        message=message,
        from_email='noreply@swahilipot.com',
        recipient_list=[email],
        fail_silently=True,
    )