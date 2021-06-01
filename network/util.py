from enum import Enum, auto
from .models import *


class FeedType(Enum):
    """Network appista löytyvät feedit."""
    ALL_POSTS = auto()
    FOLLOWING = auto()
    PROFILE = auto()


class Feed(object):
    """Käytetään index viewissä sen päättämiseen, mikä feedi käyttäjälle näytetään."""
    def __init__(self, feed=None):
        self.feed = FeedType.ALL_POSTS
        self.user_id = None

    def __repr__(self):
        try:
            return self.feed.name
        except:
            return ""

    def getFeed(self):
        try:
            return self.feed.name
        except:
            return ""

    def getUserID(self):
        return self.user_id

    def setFeed(self, feed):
        assert feed in FeedType
        self.feed = feed

    def getOptions(self):
        options = []
        for feed in FeedType:
            options.append(feed)
        return options

    def setFeedToAll(self):
        temp_enum = FeedType
        self.feed = temp_enum.ALL_POSTS

    def setFeedToFollow(self):
        temp_enum = FeedType
        self.feed = temp_enum.FOLLOWING

    def setFeedToProfile(self, user_id):
        temp_enum = FeedType
        self.feed = temp_enum.PROFILE
        self.user_id = user_id


def getFollowedPosts(user_id):
    """Palauttaa kaikki postaukset käyttäjiltä, jotka käyttäjä (user_id) on laittanut
    seurantaan."""
    user = User.objects.get(pk=user_id)
    followed_user_ids = []
    for follow in user.follows.all():
        followed_user_ids.append(follow.followed)
    followed_posts = Post.objects.filter(user__in=followed_user_ids)
    return followed_posts


def getUsersPosts(user_id):
    """Palauttaa kaikki postaukset käyttäjältä user_id."""
    user = User.objects.get(pk=user_id)
    posts = Post.objects.filter(user=user)
    return posts

