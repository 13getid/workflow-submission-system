from django.shortcuts import render, redirect
from .forms import SubmissionForm

# Create your views here.
def home(request):
    return render(request, 'submissions/home.html')

def submit(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = SubmissionForm()
    return render(request, 'submissions/submit.html', {'form': form})

def success(request):
        return render(request, 'submissions/success.html')