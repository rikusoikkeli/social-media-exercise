from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django import forms

from .models import User, Follow, Post, Comment, Like


class PostCommentForm(forms.Form):
    content = forms.CharField(label=False)
    post_id = forms.CharField(widget=forms.HiddenInput())
    page = forms.CharField(widget=forms.HiddenInput())


def index(request):
    if request.method == "POST":
        form = PostCommentForm(request.POST)
        if form.is_valid():
            user = request.user
            post_id = form.cleaned_data["post_id"]
            content = form.cleaned_data["content"]
            page_number = form.cleaned_data["page"]
            post = Post.objects.get(pk=post_id)

            new_comment = Comment(user=user, content=content, post=post)
            new_comment.save()

            # Tehdään tämä, jotta palataan samalle Paginator-sivulle, jolla oltiin aiemmin.
            url = reverse("index")+"?page="+str(page_number)
            return HttpResponseRedirect(url)
        else:
            return HttpResponse("Form is not valid!")
    else:
        posts = Post.objects.all().order_by('-id')
        # Paginator params: iterable, objects per page
        posts_paginated = Paginator(posts, 3)
        # get method params: name from query string, default value if not found
        page_num = request.GET.get("page", 1)
        page = posts_paginated.page(page_num)

        comments = Comment.objects.all()
        form = PostCommentForm()

        return render(request, "network/index.html", {
            "page": page,
            "comments": comments,
            "form": form
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def getComments(request, post_id):
    
    # Query for requested comments
    try:
        post = Post.objects.get(pk=post_id)
        comments = Comment.objects.filter(post=post)
    except Comment.DoesNotExist:
        return JsonResponse({"error": "Comments not found."}, status=404)

    # Return comments
    if request.method == "GET":
        # Miksi tämä toimii?
        return JsonResponse([comment.serialize() for comment in comments], safe=False)

