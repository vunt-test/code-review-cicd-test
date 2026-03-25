import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Campaign, Post


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


class CampaignCreateAPITest(TestCase):
    def test_create_campaign_success(self):
        payload = {
            'name': 'Spring Launch',
            'description': 'Campaign description',
            'objective': 'Increase awareness',
            'channels': ['facebook', 'email'],
            'status': 'draft',
            'start_date': '2026-04-01',
            'end_date': '2026-04-30',
            'budget': '1000.50',
        }
        response = self.client.post(
            reverse('create_campaign'),
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], payload['name'])
        self.assertEqual(Campaign.objects.count(), 1)

    def test_create_campaign_invalid_json(self):
        response = self.client.post(
            reverse('create_campaign'),
            data='not-json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_create_campaign_missing_name(self):
        response = self.client.post(
            reverse('create_campaign'),
            data=json.dumps({'description': 'x'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


class UserManagementAPITest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.normal_user = User.objects.create_user(
            username='normal',
            email='normal@example.com',
            password='normal-pass',
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin-pass',
        )
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()

    def test_user_create_success(self):
        self.client.force_login(self.admin_user)

        payload = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
        }
        response = self.client.post(
            reverse('users_list_create'),
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['username'], payload['username'])
        self.assertEqual(data['email'], payload['email'])

        User = get_user_model()
        created_user = User.objects.get(username=payload['username'])
        self.assertTrue(created_user.check_password(payload['password']))

    def test_user_list_forbidden_non_admin(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(reverse('users_list_create'))
        self.assertEqual(response.status_code, 403)

    def test_user_update_success(self):
        User = get_user_model()
        target = User.objects.create_user(
            username='target',
            email='target@example.com',
            password='oldpass',
        )
        self.client.force_login(self.admin_user)

        payload = {
            'email': 'target2@example.com',
            'password': 'newpass456',
        }
        response = self.client.patch(
            reverse('user_detail_update_delete', args=[target.id]),
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)

        target.refresh_from_db()
        self.assertEqual(target.email, payload['email'])
        self.assertTrue(target.check_password(payload['password']))

    def test_user_delete_success(self):
        User = get_user_model()
        target = User.objects.create_user(
            username='todelete',
            email='todelete@example.com',
            password='pass123',
        )
        self.client.force_login(self.admin_user)

        response = self.client.delete(
            reverse('user_detail_update_delete', args=[target.id]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['deleted'], True)
        self.assertFalse(User.objects.filter(id=target.id).exists())

    def test_user_create_invalid_payload(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse('users_list_create'),
            data=json.dumps({'username': 'x', 'email': 'x@example.com'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
