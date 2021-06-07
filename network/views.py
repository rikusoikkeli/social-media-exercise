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
from .util import FeedType, Feed, getFollowedPosts, getUsersPosts, composeInfoAboutLikes


class PostCommentForm(forms.Form):
    content = forms.CharField(label=False)
    post_id = forms.CharField(widget=forms.HiddenInput())
    page = forms.CharField(widget=forms.HiddenInput())


class MakeNewPostForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={"placeholder":"What's on your mind?"}), label=False)


def index(request, feed=Feed()):
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

    if request.method == "GET":
        user_viewing_own_profile = False
        profile_user = None
        try:
            if feed.getFeed() == "ALL_POSTS":
                posts = Post.objects.all().order_by('-id')
            elif feed.getFeed() == "FOLLOWING" and request.user.is_authenticated:
                posts = getFollowedPosts(request.user.id).order_by('-id')
            elif feed.getFeed() == "PROFILE":
                profile_user = User.objects.get(pk=feed.getUserID())
                posts = getUsersPosts(profile_user.pk).order_by('-id')
        except:
            return HttpResponse("User could not be found!", status=404)

        # Paginator params: iterable, objects per page
        posts_paginated = Paginator(posts, 3)
        # get method params: name from query string, default value if not found
        page_num = request.GET.get("page", 1)
        page = posts_paginated.page(page_num)

        comments = Comment.objects.all()
        comment_form = PostCommentForm()
        new_post_form = MakeNewPostForm()

        return render(request, "network/index.html", {
            "page": page,
            "comments": comments,
            "comment_form": comment_form,
            "new_post_form": new_post_form,
            "feed_to_show": feed.getFeed(),
            "profile_user": profile_user
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
    except:
        return JsonResponse({"error": "Comments not found."}, status=404)

    # Return comments
    if request.method == "GET":
        return JsonResponse([comment.serialize() for comment in comments], safe=False)


@csrf_exempt
@login_required
def getPost(request, post_id):

    # Haetaan postaus
    try:
        post = Post.objects.get(pk=post_id)
    except:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Jos request method on GET, palautetaan postaus JSON-muodossa
    if request.method == "GET":
        post_serialized = post.serialize()
        user_id = request.user.id
        if user_id in post_serialized["like_user_ids"]:
            post_serialized["current_user_likes"] = True
        else:
            post_serialized["current_user_likes"] = False

        # Lisätään tähän selitys tykkäyksistä, jota käytetään Like-painikkeen vieressä
        post_serialized["like_text"] = composeInfoAboutLikes(post_serialized["like_user_ids"])

        return JsonResponse(post_serialized, safe=False)

    # Jos request method on PUT, tehdään jokin useammasta vaihtoehdosta...
    if request.method == "PUT":
        data = json.loads(request.body)
        if "like" in data:
            if data.get("like") == True:
                # Jos like on True, yritetään lisätä Like. Annetaan lopputuloksesta statuskoodi.
                try:
                    like = Like(user=request.user, post=post)
                    like.save()
                    return HttpResponse(status=204)
                except:
                    return JsonResponse({"error": "Could not add Like"}, status=404)
            elif data.get("like") == False:
                # Jos like ei ole True (eli on False), poistetaan Like. Annetaan lopputuloksesta statuskoodi.
                try:
                    like = Like.objects.get(user=request.user, post=post)
                    like.delete()
                    return HttpResponse(status=204)
                except:
                    return JsonResponse({"error": "Could not remove Like"}, status=404)
        # alle uusi koodi
        elif "edited_post" in data:
            try:
                post.content = data.get("edited_post")
                post.save(["content"])
                return HttpResponse(status=204)
            except:
                return JsonResponse({"error": "Could not edit Post"}, status=404)
        elif "delete" in data:
            try:
                post.delete()
                return HttpResponse(status=204)
            except:
                return JsonResponse({"error": "Could not delete Post"}, status=404)


@login_required
def makeNewPost(request):
    if request.method == "POST":
        try:
            # yritetään tehdä ja tallentaa postaus
            form = MakeNewPostForm(request.POST)
            if form.is_valid():
                user = request.user
                content = form.cleaned_data["content"]
                newPost = Post(user=user, content=content)
                newPost.save()
            else:
                raise Exception("Not valid data!")
        except:
            # palautetaan error
            return HttpResponse("Something went wrong!")
        # ohjataan etusivulle
        return HttpResponseRedirect(reverse("network:index"))


@csrf_exempt
@login_required
def userData(request, user_id):
    # kokeillaan, onko käyttäjä olemassa
    try:
        user = User.objects.get(pk=user_id)
    except:
        return JsonResponse({"error": "User not found."}, status=404)
    
    if request.method == "GET":
        user_serialized = user.serialize()
        # jos käyttäjä hakee itsensä tiedot, ei alla olevaa kenttää, jotta JS ei laita nappia
        # lisätään myös current_user_is_user bool
        if request.user.id != user_serialized["user_id"]:
            user_serialized["current_user_is_user"] = False
            # kokeillaan, onko requestin lähettäjä dictissä user_is_followed by
            try:
                user_serialized["user_is_followed_by"][request.user.id]
                user_serialized["current_user_follows"] = True
            except:
                user_serialized["current_user_follows"] = False
        else:
            user_serialized["current_user_is_user"] = True

        return JsonResponse(user_serialized, safe=False) 

    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("current_user_follows") == True:
            try:
                print(f"set user {request.user.username} to follow {user.username}")
                newFollow = Follow(follower=request.user, followed=user)
                newFollow.save()
                return HttpResponse(status=204)
            except:
                return JsonResponse({"error": "Could not add Follow"}, status=404)
        else:
            try:
                print(f"set user {request.user.username} to unfollow {user.username}")
                Follow.objects.get(follower=request.user, followed=user).delete()
                return HttpResponse(status=204)
            except:
                return JsonResponse({"error": "Could not remove Follow"}, status=404)


def followingFeed(request):
    feed=Feed()
    feed.setFeedToFollow()
    return index(request, feed)


def profileView(request, user_id):
    if request.user.is_authenticated:
        feed=Feed()
        feed.setFeedToProfile(user_id)
        return index(request, feed)
    else:
        return HttpResponse("Something went wrong!")

