from django.test import TestCase
from django.urls import reverse

from .models import Post


class PostModelTest(TestCase):
    def setUp(self):
        self.post = Post.objects.create(
            title='Test Post',
            content='This is test content.',
        )

    def test_post_str(self):
        self.assertEqual(str(self.post), 'Test Post')

    def test_post_fields(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.content, 'This is test content.')
        self.assertIsNotNone(self.post.created_at)


class PostViewTest(TestCase):
    def setUp(self):
        self.post = Post.objects.create(
            title='Hello World',
            content='Welcome to my blog.',
        )

    def test_post_list_view(self):
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello World')

    def test_post_detail_view(self):
        response = self.client.get(reverse('post_detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello World')
        self.assertContains(response, 'Welcome to my blog.')

    def test_post_detail_not_found(self):
        response = self.client.get(reverse('post_detail', args=[999]))
        self.assertEqual(response.status_code, 404)
