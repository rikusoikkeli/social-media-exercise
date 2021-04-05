from enum import Enum, auto
from .models import *


class FeedType(Enum):
    """Network appista löytyvät feedit."""
    ALL_POSTS = auto()
    FOLLOWING = auto()


class Feed(object):
    """Käytetään index viewissä sen päättämiseen, mikä feedi käyttäjälle näytetään."""
    def __init__(self, feed=None):
        self.feed = FeedType.ALL_POSTS

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


def getFollowedPosts(user_id):
    """Palauttaa kaikki postaukset käyttäjiltä, jotka käyttäjä (user_id) on laittanut
    seurantaan."""
    user = User.objects.get(pk=user_id)
    followed_user_ids = []
    for follow in user.follows.all():
        followed_user_ids.append(follow.followed)
    followed_posts = Post.objects.filter(user__in=followed_user_ids)
    return followed_posts

