from django.urls import path,include
from account.views import login_user,register_user,home_page

urlpatterns = [
  path("register/",register_user,name = "register-user"),
  path("login/",login_user,name = "login-user"),
  path("",home_page,name="home-page")
]