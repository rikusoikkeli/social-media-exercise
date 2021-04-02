from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime


class User(AbstractUser):
    photo = models.ImageField(upload_to="network/static/network/photos", blank=True)

    def __str__(self):
        return f"{self.username}"


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name="follower")
    followed = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name="followed")

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
            "user_id": self.user.id,
            "post_id": self.post.id,
            "content": self.content,
            "time": self.time
        }


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=False)

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

