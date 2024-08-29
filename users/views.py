from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ResumeForm, UserUpdateForm
from .models import Resume
from django.http import FileResponse, Http404
from django.contrib.auth import get_user_model

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            print("Redirecting to dashboard")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('dashboard')  
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    user = request.user
    try:
        resume = Resume.objects.get(user=user)
    except Resume.DoesNotExist:
        resume = None

    if request.method == 'POST':
        if 'delete_account' in request.POST:
            user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('home')  # Redirect to home or another page
        elif 'update_profile' in request.POST:
            form = UserUpdateForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile has been updated!')
                return redirect('dashboard')  # Redirect to dashboard or another page

    form = UserUpdateForm(instance=user)
    
    context = {
        'resume': resume,
        'form': form,
    }
    return render(request, 'dashboard.html', context)

def home(request):
    return render(request, 'users/home.html')



@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume, created = Resume.objects.get_or_create(user=request.user)
            resume.file = form.cleaned_data['file']
            resume.save()
            return redirect('dashboard')  # Redirect to dashboard or another appropriate page
    else:
        form = ResumeForm()
    return render(request, 'users/upload_resume.html', {'form': form})

@login_required
def update_resume(request):
    resume = get_object_or_404(Resume, user=request.user)
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES, instance=resume)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ResumeForm(instance=resume)
    return render(request, 'users/update_resume.html', {'form': form})

@login_required
def delete_resume(request):
    resume = get_object_or_404(Resume, user=request.user)
    if request.method == 'POST':
        resume.delete()
        return redirect('dashboard')
    return render(request, 'users/confirm_delete_resume.html', {'resume': resume})


@login_required
def download_resume(request):
    resume = get_object_or_404(Resume, user=request.user)
    file_path = resume.file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=resume.file.name)
    except FileNotFoundError:
        raise Http404("Resume file not found")
    
    
    

User = get_user_model()

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('dashboard')
    else:
        form = UserUpdateForm(instance=user)
    
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def delete_account(request):
    user = request.user
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('home')  
    return render(request, 'users/confirm_delete_account.html')