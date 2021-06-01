
from django.urls import path

from . import views


app_name = "network"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("comments/<int:post_id>", views.getComments, name="getComments"),
    path("post/<int:post_id>", views.getPost, name="getPost"),
    path("new", views.makeNewPost, name="makeNewPost"),
    path("data/user/<int:user_id>", views.userData, name="userData"),
    path("following", views.followingFeed, name="followingFeed"),
    path("profile/<int:user_id>", views.profileView, name="profileView")
]

