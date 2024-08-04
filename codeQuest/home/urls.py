from django.urls import path,include
from home.views import logout_user,home_page,problem_page,leaderboard,submit,run,profile

urlpatterns = [
  path("logout/",logout_user,name = "logout_user"),
  path("home/",home_page,name = "home-page"),
  path("problem/<str:name>/",problem_page,name="problem_page"),
  path("leaderboard/",leaderboard,name="leader_board"),
  path("submit/<str:ques_name>/", submit, name="submit_code"),
  path("run/", run, name="run_code"),
  path("profile/",profile,name="profile_view")
]