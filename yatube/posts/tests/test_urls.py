from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post
from http import HTTPStatus
from django.core.cache import cache

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Это тестовый текст длинною больше 15 символов',
        )
        cls.index = '/'
        cls.group = '/group/test-slug/'
        cls.profile = '/profile/auth/'
        cls.post_detail = '/posts/1/'
        cls.edit = '/posts/1/edit/'
        cls.create = '/create/'
        cls.nonexist_page = '/nonexist-page/'

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_author = Client()
        self.not_author.force_login(self.user2)

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_url_names = {
            self.index: 'posts/index.html',
            self.group: 'posts/group_list.html',
            self.profile: 'posts/profile.html',
            self.post_detail: 'posts/post_detail.html',
            self.edit: 'posts/create.html',
            self.create: 'posts/create.html',
            self.nonexist_page: 'core/404.html',

        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_at_desired_locations(self):
        """Страницы доступны любому пользователю."""
        urls = [
            self.index,
            self.group,
            self.profile,
            self.post_detail
        ]
        for address in urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(self.create)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get(self.create, follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next={self.create}'
        )

    def test_unexisting_page(self):
        """Несуществующая страница вернет ошибку 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_edit_url_exists_at_desired_location(self):
        """Страница /edit/ доступна автору."""
        response = self.authorized_client.get(self.edit)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_not_exists_not_author(self):
        """Страница /edit/ не доступна не автору."""
        response = self.not_author.get(
            self.edit, follow=True
        )
        self.assertRedirects(
            response, self.post_detail
        )
