from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import SubmissionForm
from .models import Submission
from django.contrib.admin.views.decorators import staff_member_required
# Create your views here.
def home(request):
    return render(request, 'submissions/home.html')

def submit(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            Submission = form.save(commit=False)
            Submission.user = request.user
            Submission.save()
            return redirect('dashboard')
        else:
            print("FROM ERRORS:", form.errors)
    else:
        form = SubmissionForm()
    return render(request, 'submissions/submit.html', {'form': form})

def success(request):
    return render(request, 'submission/success.html')
@login_required
def dashboard(request):
    submissions = Submission.objects.filter(user=request.user).order_by('-submitted_at')
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

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'submissions/login.html', {'error': True})
    return render(request, 'submissions/login.html')

def register_view(request):
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

@staff_member_required(login_url='login')
def admin_dashboard(request):
    submissions = Submission.objects.all().order_by('-submitted_at')
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
    return render(request, 'submissions/admin_dashboard.html', context)

@staff_member_required(login_url='login')
def update_status(request, submission_id):
    if request.method == 'POST':
        submission = Submission.objects.get(id=submission_id)
        submission.status = request.POST['status']
        submission.save()
    return redirect('admin_dashboard')
