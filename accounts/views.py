from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data["password"])
            new_user.save()
            return render(request, "accounts/register_done.html", {"new_user": new_user})
    else:
        form = UserRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})

def user_login(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd["username"], password=cd["password"])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("dashboard")
                else:
                    return render(request, "accounts/login.html", {"form": form, "error": "Disabled account"})
            else:
                return render(request, "accounts/login.html", {"form": form, "error": "Invalid login"})
    else:
        form = UserLoginForm()
    return render(request, "accounts/login.html", {"form": form})

@login_required
def profile(request):
    return render(request, "accounts/profile.html", {"section": "profile"})

def user_logout(request):
    logout(request)
    return redirect("login")
