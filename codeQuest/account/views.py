from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
#from .models import user_data  # Import the user_data model

def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.filter(username=username)
        if user.exists():
            messages.info(request, 'User with this username already exists')
            return redirect("/register/")
        
        if not email.endswith('@gmail.com'):
            messages.info(request,"Email must end with @gmail.com")
            return redirect("/register/")
        
        if len(password) < 8:
          messages.info(request,"password should be atleast 8 characters")
          return redirect("/register/")
           

        user = User.objects.create_user(username=username)
        user.set_password(password)
        user.email=email
        user.save()

        # Create a new user_data object and save it
        
        
        # user_data_obj = user_data.objects.create(
        #     user=user,
        #     email=email
        # )
        #user_data_obj.save()

        messages.info(request, 'User created successfully')
        return redirect("/login")

    template = loader.get_template('register.html')
    context = {}
    return HttpResponse(template.render(context, request))

def login_user(request):
  if request.method == "POST":
    username = request.POST.get('username')
    password = request.POST.get('password')

    if not User.objects.filter(username = username).exists():
      messages.info(request,'User does not exists')
      return redirect('/login')
    
    user = authenticate(username = username,password = password)

    if user is None:
      messages.info(request,'Invalid passowrd')
      return redirect('/login/')
    
    login(request,user)
    
    return redirect('/home/')
  
  template = loader.get_template('login.html')
  
  context = {}
  return HttpResponse(template.render(context,request))

def home_page(request):
  template = loader.get_template('home_page.html')
  context = {}
  return HttpResponse(template.render(context, request))

