from django.shortcuts import redirect, render
from .forms import CustomUserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model

#Note: 
#   1. The user model is set to CustomUser in settings.py
#   2. request.session['login_status'] is used to store the login status to be used in templates
#   3. request.session['login_status'] is set to false initally in middleware 

def login_view(request):

    if request.method == 'POST':
        UserModel = get_user_model() #gets CustomUser
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        #Check if all fields are entered
        if not email and not password:
            return render(request, "users/login.html", {"error": "Please enter an email and a password."})
        elif not email:
            return render(request, "users/login.html", {"error": "Please enter a valid email."})
        elif not password:
            return render(request, "users/login.html", {"error": "Please enter a password."})
        
        try:
            user = UserModel.objects.get(email = email)
            print(user)
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                request.session['login_status'] = True

                # Redirect superusers to the admin UI
                if user.is_superuser:
                    return redirect('/admin/')
                
                # Redirect regular users to the shop index page
                return redirect("shop:index")
            else:
                return render(request, "users/login.html", {"error": "Invalid credentials"})
        except UserModel.DoesNotExist:
            #The entered email was wrong or invalid
            return render(request, "users/login.html", {"error": "Invalid credentials"})
            
    # if not logged in just a get request:   
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)  # Logs the user out and clears the session
    request.session['login_status'] = False 
    return redirect('users:login') 

def register_view(request):
    form = CustomUserForm()
    #check if the form is submitted to validate, save requests if valid and display error messages otherwise
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session['login_status'] = True
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('shop:index')  # Redirects to 'index' instead of rendering the same page
        else:
            #Unsuccessful register, go back to register.html
            return render(request, 'users/register.html', {'form': form})
        
    context = {"form" : form}
    return render(request, 'users/register.html', context)
