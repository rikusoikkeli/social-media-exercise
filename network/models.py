from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime


class User(AbstractUser):
    photo = models.ImageField(upload_to="network/static/network/photos", blank=True)

    def __str__(self):
        return f"{self.username}"

    def getStaticURL(self):
        """Pelkkä user.photo.url antaa liian pitkän urlin. Ei sovi Django-templateen. 
        Tämä funktio palauttaa urlin static-kansiosta eteenpäin."""
        try:
            url = self.photo.url
            url_split = url.split("static")
            url_static = "/static" + url_split[-1]
            return url_static
        except:
            return False

    def serialize(self):
        user_follows = {}
        for user in self.follows.all():
            user_follows[user.followed.id] = user.followed.username
        user_is_followed_by = {}
        for user in self.followers.all():
            user_is_followed_by[user.follower.id] = user.follower.username       
        return {
            "user_id": self.id,
            "username": self.username,
            "photo_url": self.getStaticURL(),
            "user_follows": user_follows,
            "user_is_followed_by": user_is_followed_by
        }


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name="follows")
    followed = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name="followers")

    class Meta:
        constraints = [
            # constraint: follower != followed
            models.CheckConstraint(
                    check=~models.Q(follower=models.F('followed')), 
                    name="follower_followed_must_be_unequal")
        ]

    def __str__(self):
        return f"{self.follower} -> {self.followed}"

    def isValidFollow(self):
        if self.follower != self.followed and isinstance(self.follower, User) and isinstance(self.followed, User):
            return True
        else:
            return False


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    content = models.CharField(max_length=280, blank=False)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if len(self.content) > 20:
            return f"{self.user}: {self.content[0:19]}..."
        else:
            return f"{self.user}: {self.content}"

    def isValidPost(self):
        if isinstance(self.user, User) and isinstance(self.content, str) and isinstance(self.time, datetime.datetime):
            return True
        else:
            return False

    def serialize(self):
        # tehdään dict tykkääjistä
        likes_list = []
        for like in self.likes.all():
            likes_list.append(like.user.id)
        # tehdään dict postauksesta, johon lisätään tykkääjät
        post_dict = {
            "post_id": self.id,
            "post_content": self.content,
            "post_time": str(self.time),
            "like_user_ids": likes_list
        }
        # palautetaan dict
        return post_dict


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    content = models.CharField(max_length=280, blank=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=False)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if len(self.content) > 20:
            return f"{self.user}: {self.content[0:19]}..."
        else:
            return f"{self.user}: {self.content}"

    def isValidComment(self):
        if (isinstance(self.user, User) and isinstance(self.content, str) and isinstance(self.post, Post) and 
        isinstance(self.time, datetime.datetime)):
            return True
        else:
            return False

    def serialize(self):
        return {
            "comment_id": self.id,
            "comment_content": self.content,
            "user_id": self.user.id,
            "user_username": self.user.username,
            "user_photo": str(self.user.getStaticURL()),
            "post_id": self.post.id,
            "time": self.time
        }


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=False, related_name="likes")

    class Meta:
        constraints = [
            # sallitaan käyttäjältä vain yksi tykkäys per postaus
            models.UniqueConstraint(fields=["user", "post"], name="user_post_must_be_unique"),
        ]

    def __str__(self):
        return f"{self.user} -> post({self.post.id})"

    def isValidLike(self):
        if isinstance(self.user, User) and isinstance(self.post, Post):
            return True
        else:
            return False

