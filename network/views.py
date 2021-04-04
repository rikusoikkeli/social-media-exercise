from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import User, Follow, Post, Comment, Like


class PostCommentForm(forms.Form):
    content = forms.CharField(label=False)
    post_id = forms.CharField(widget=forms.HiddenInput())
    page = forms.CharField(widget=forms.HiddenInput())


class MakeNewPostForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={"placeholder":"What's on your mind?"}), label=False)


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
            url = reverse("network:index")+"?page="+str(page_number)
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

        form2 = MakeNewPostForm()

        return render(request, "network/index.html", {
            "page": page,
            "comments": comments,
            "form": form,
            "form2": form2
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
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


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
        return HttpResponseRedirect(reverse("network:index"))
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
        return JsonResponse([comment.serialize() for comment in comments], safe=False)


@csrf_exempt
@login_required
def getPost(request, post_id):

    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    # Testaa mikä tämän except-blokin logiikka on
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method == "GET":
        post_serialized = post.serialize()
        user_id = request.user.id
        if user_id in post_serialized["like_user_ids"]:
            post_serialized["current_user_likes"] = True
        else:
            post_serialized["current_user_likes"] = False

        return JsonResponse(post_serialized, safe=False)

    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("like") == True:
            # Jos like on True, yritetään lisätä Like. Annetaan lopputuloksesta statuskoodi.
            try:
                like = Like(user=request.user, post=post)
                like.save()
                return HttpResponse(status=204)
            except:
                return JsonResponse({"error": "Could not add Like"}, status=404)
        else:
            # Jos like ei ole True (eli on False), poistetaan Like. Annetaan lopputuloksesta statuskoodi.
            try:
                like = Like.objects.get(user=request.user, post=post)
                like.delete()
                return HttpResponse(status=204)
            except:
                return JsonResponse({"error": "Could not remove Like"}, status=404)


@login_required
def makeNewPost(request):
    if request.method == "POST":
        try:
            # yritetään tehdä ja tallentaa postaus
            form = MakeNewPostForm(request.POST)
            if form.is_valid():
                user = request.user
                content = form.cleaned_data["content"]
                print(content)
                newPost = Post(user=user, content=content)
                newPost.save()
                print("käyttäjä tallensi postauksen")
            else:
                raise Exception("Not valid data!")
        except:
            # palautetaan error
            print("jokin meni pieleen")
        # ohjataan etusivulle
        return HttpResponseRedirect(reverse("network:index"))
