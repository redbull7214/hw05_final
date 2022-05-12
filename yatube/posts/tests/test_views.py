import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from ..models import Group, Post, Follow
from django.urls import reverse
from django import forms
from django.core.cache import cache

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.img_user = User.objects.create_user(username='img_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа-2',
            slug='test-slug-2',
            description='Тестовое описание-2',
        )
        cls.empty_group = Group.objects.create(
            title='Тестовая группа-3',
            slug='test-slug-3',
            description='Тестовое описание пустой группы',
        )
        cls.group_image = Group.objects.create(
            title='Тестовая группа с изображением',
            slug='test-slug-img',
            description='Тестовое описание с изображением',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Это тестовый текст длинною больше 15 символов',
            group=cls.group
        )
        cls.post2 = Post.objects.create(
            author=cls.user2,
            text='Это тестовый текст №2 длинною больше 15 символов',
            group=cls.group2
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post_image = Post.objects.create(
            author=cls.img_user,
            text='Тестовый пост с изображением длиною 30 символов',
            image=cls.uploaded,
            group=cls.group_image,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.unfollowed_client = Client()
        self.unfollowed_client.force_login(self.user2)

    def test_pages_have_image(self):
        """В шаблоны index, profile, group_list передается изображение."""
        templates = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug-img'}),
            reverse('posts:profile', kwargs={'username': 'img_user'}),
        }
        for template in templates:
            with self.subTest(template=template):
                url = template
                response = self.authorized_client.get(url)
                content = response.context.get("page_obj")
                for cont in content:
                    with self.subTest(cont=cont):
                        if cont.image:
                            self.assertNotEqual(len(cont.image), 0)

    def test_post_detail_have_image(self):
        """В шаблон post_detail передается изображение"""
        url = reverse('posts:post_detail', kwargs={
            'post_id': f'{self.post_image.id}'
        })
        response = self.authorized_client.get(url)
        content = response.context.get("post")
        if content.image:
            self.assertNotEqual(len(content.image), 0)

    def test_follow_and_unfollow(self):
        """Авторизованный пользователь может подписываться на других
         пользователей и удалять их из подписок.
         """
        self.authorized_client.get(reverse('posts:profile_follow', kwargs={
            'username': 'auth'
        }))
        self.assertFalse(Follow.objects.all().exists())
        self.authorized_client.get(reverse('posts:profile_follow', kwargs={
            'username': 'auth2'
        }))
        self.assertTrue(Follow.objects.all().exists())
        self.authorized_client.get(reverse('posts:profile_unfollow', kwargs={
            'username': 'auth2'
        }))
        self.assertFalse(Follow.objects.all().exists())

    def test_news_for_followers(self):
        """Новая запись пользователя появляется в ленте тех, кто
        на него подписан и не появляется в ленте тех, кто не подписан.
        """
        self.authorized_client.get(reverse('posts:profile_follow', kwargs={
            'username': 'auth2'
        }))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertContains(
            response, 'Это тестовый текст №2 длинною больше 15 символов'
        )
        response = self.unfollowed_client.get(reverse('posts:follow_index'))
        self.assertNotContains(
            response, 'Это тестовый текст №2 длинною больше 15 символов'
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            (
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            ): 'posts/group_list.html',
            (
                reverse('posts:profile', kwargs={'username': 'auth'})
            ): 'posts/profile.html',
            (
                reverse('posts:post_detail', kwargs={
                    'post_id': f'{self.post.id}'
                })
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create.html',
            (
                reverse('posts:post_edit', kwargs={
                    'post_id': f'{self.post.id}'
                })
            ): 'posts/create.html'
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertContains(
            response,
            'Это тестовый текст №2 длинною больше 15 символов'
        )
        self.assertContains(
            response,
            'Тестовая группа-2'
        )

    def test_index_page_caches(self):
        """Кеширование на главной странице работает правильно."""
        Post.objects.create(
            author=self.img_user,
            text='Тестовый пост для кеширования',
        )
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertContains(response, 'Тестовый пост для кеширования')
        Post.objects.filter(
            text='Тестовый пост для кеширования'
        ).delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertContains(response, 'Тестовый пост для кеширования')
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotContains(response, 'Тестовый пост для кеширования')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list', kwargs={
                        'slug': 'test-slug-2'
                    })))
        self.assertEqual(response.context.get(
            'group').title, 'Тестовая группа-2')
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        self.assertEqual(
            task_text_0,
            'Это тестовый текст №2 длинною больше 15 символов'
        )

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:profile', kwargs={
                        'username': 'auth2'
                    })))
        first_object = response.context['page_obj'][0]
        task_author = first_object.author.username
        task_group = first_object.group.title
        self.assertEqual(task_author, 'auth2')
        self.assertEqual(task_group, 'Тестовая группа-2')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail', kwargs={
                        'post_id': f'{self.post2.id}'
                    })))
        self.assertEqual(response.context.get('post').id, 2)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_create')))
        form_fields = {

            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,

        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_edit', kwargs={
                        'post_id': f'{self.post.id}'
                    })))
        form_fields = {

            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,

        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context.get('is_edit'), True)

    def test_empty_group(self):
        """Шаблон group_list не имеет постов у страницы новой группы."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list', kwargs={
                        'slug': 'test-slug-3'
                    })))

        first_object = len(response.context['page_obj'])
        self.assertIs(first_object, 0)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        number_of_posts = 13
        for post in range(number_of_posts):
            Post.objects.create(
                author=cls.user, text='Это тестовый текст', group=cls.group)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

    def test_paginator(self):
        """Пагинация для 13 постов работает правильно."""
        templates = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'})
        ]

        for value in templates:
            with self.subTest(value=value):
                response = self.client.get(value)
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.client.get(value + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
