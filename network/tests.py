from django.test import TestCase
from .models import User, Follow, Post, Comment, Like
import datetime

# Create your tests here.
class NetworkTestCase(TestCase):

    def setUp(self):

        #users
        u1 = User.objects.create(username="Harry")
        u2 = User.objects.create(username="Ron")
        u3 = User.objects.create(username="Hermione")
        #follows
        f1 = Follow.objects.create(follower=u1, followed=u2)
        f2 = Follow.objects.create(follower=u2, followed=u1)
        #posts
        p1 = Post.objects.create(user=u1, content="Hello! This is my first social media post!")
        p2 = Post.objects.create(user=u1, content="Hello! This is my second social media post!")
        p3 = Post.objects.create(user=u2, content="Hello!")
        #comments
        c1 = Comment.objects.create(user=u1, content="I'm commenting my own post!", post=p1)
        c2 = Comment.objects.create(user=u2, content="I'm commenting my friend's post!", post=p1)
        #likes
        l1 = Like.objects.create(user=u1, post=p1)
        l2 = Like.objects.create(user=u2, post=p3)


    def testUsersCount(self):
        all_users_count = len(User.objects.all())
        self.assertEqual(all_users_count, 3)

    def testFollowCount(self):
        all_follows_count = len(Follow.objects.all())
        self.assertEqual(all_follows_count, 2)

    def testPostsCount(self):
        all_posts_count = len(Post.objects.all())
        self.assertEqual(all_posts_count, 3)

    def testCommentsCount(self):
        all_comments_count = len(Comment.objects.all())
        self.assertEqual(all_comments_count, 2)

    def testLikesCount(self):
        all_likes_count = len(Like.objects.all())
        self.assertEqual(all_likes_count, 2)

    def testValidFollow(self):
        follow = Follow.objects.all()[0]
        self.assertTrue(follow.isValidFollow())

    def testValidPost(self):
        post = Post.objects.all()[0]
        self.assertTrue(post.isValidPost())

    def testValidComment(self):
        comment = Comment.objects.all()[0]
        self.assertTrue(comment.isValidComment())
        
    def testValidLike(self):
        like = Like.objects.all()[0]
        self.assertTrue(like.isValidLike())

