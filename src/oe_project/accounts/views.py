from django.contrib.auth.backends import UserModel
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import update_session_auth_hash

from .forms import UserBioForm, UserAvatarForm, UserProfileForm, UserPasswordForm

# Create your views here.
brand = 'DONGJIN VIETNAM J.S.C'


def login_failed(request):
    messages.add_message(request, messages.ERROR,
                         'Username or Password is incorrect')


def loginPage(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get('next', 'home'))
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(request.GET.get('next', 'home'))
            else:  # Login with email as username
                user_mail = ''
                try:
                    user_mail = User.objects.get(email=username)
                    user = authenticate(
                        request, username=user_mail.username, password=password)
                    if user is not None:
                        login(request, user)
                        return redirect(request.GET.get('next', 'home'))
                    else:
                        login_failed(request)
                except:
                    login_failed(request)

    return render(request, 'login.html')


def logoutPage(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def profiles(request, username):
    title = 'Profiles'
    user = request.user
    bio_form = UserBioForm()
    avatar_form = UserAvatarForm()

    if request.method == 'POST':
        if 'btn-change-bio' in request.POST:
            form = UserBioForm(request.POST, instance=user)
            if form.is_valid():
                form.save()

        if 'btn-change-avatar' in request.POST:
            form = UserAvatarForm(request.POST, request.FILES, instance=user)
            print(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('profiles', username=username)

    context = {
        'brand': brand,
        'title': title,
        'bio_form': bio_form,
        'avatar_form': avatar_form,
    }
    return render(request, 'profiles.html', context=context)


@login_required(login_url='login')
def settings(request, username):
    title = 'Settings & Privacy'
    user = request.user
    password_form = UserPasswordForm()
    profile_form = UserProfileForm()

    if request.method == 'POST':
        if 'save-password' in request.POST:
            form = UserPasswordForm(request.POST, instance=user)
            if form.is_valid():
                setting = form.save(commit=False)
                current_password = form.cleaned_data['current_password']
                # Check user current password
                if check_password(current_password, user.password):
                    new_password = form.cleaned_data['new_password']
                    confirm_password = form.cleaned_data['confirm_password']
                    if new_password == confirm_password:
                        # Hash password
                        setting.password = make_password(new_password)
                        setting.save()
                        # Keep session when user change password
                        update_session_auth_hash(request, user)
                        messages.add_message(
                            request, messages.SUCCESS, 'Password update successfully.')

                    else:
                        messages.add_message(
                            request, messages.ERROR, "Password confirmation doesn't match password.")
                else:
                    messages.add_message(
                        request, messages.ERROR, 'Invalid password.')

        if 'save-profile' in request.POST:
            form = UserProfileForm(request.POST, instance=user)

            if form.is_valid():
                form.save()
                messages.add_message(
                    request, messages.SUCCESS, 'Profile updated.')
            else:
                messages.add_message(
                    request, messages.ERROR, 'Form is invalid.')

    context = {
        'brand': brand,
        'title': title,
        'password_form': password_form,
        'profile_form': profile_form,
    }
    return render(request, 'settings.html', context=context)
