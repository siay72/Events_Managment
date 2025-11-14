from django.shortcuts import render, redirect
from users.forms import CustomRegistrationForm, LoginForm
from django.contrib import messages
from django.contrib.auth import  login,logout



# Create your views here.


'''User Register'''


def sign_up(request):
    form = CustomRegistrationForm()
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1')) 
            user.is_active = False
            user.save()
            messages.success(
                request, 'A Confirmation mail sent. Please check your email')
            return redirect('sign-in')
						
						
        else:
            print("Form is not valid")
    return render(request, 'sign_user/sign_up.html', {"form": form})




'''User Login'''

def sign_in(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    return render(request, 'sign_user/login.html', {'form': form})


def sign_out(request):
    if request.method == "POST":
        logout(request)
        return redirect('home')
    return redirect('home')