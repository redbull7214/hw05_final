import shutil
import tempfile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.forms import PostForm
from ..models import Group, Post, Comment
from ..forms import CommentForm, PostForm
from django.urls import reverse
from django.core.cache import cache

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Это тестовый текст длинною больше 15 символов',
            group=cls.group
        )
        cls.form = PostForm()
        cls.comment_form = CommentForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_form_with_image(self):
        """Форма с картинкой сохраняется в БД."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': PostCreateFormTests.group.id,
            'text': 'Тестовый текст длинною более 20 символов',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:profile', kwargs={
                                 'username': PostCreateFormTests.user
                             }))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=PostCreateFormTests.group.id,
                text='Тестовый текст длинною более 20 символов',
                image='posts/small.gif'
            ).exists()
        )

    def test_post_create(self):
        """При отправке формы создаётся новая запись в базе данных."""
        form_data = {
            'text': 'Текстовый пост для создания второго поста',
            'group': PostCreateFormTests.group.id,
        }
        post_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:profile', kwargs={
                                 'username': PostCreateFormTests.user
                             }))
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_post_edit(self):
        """При редактировании формы изменяется запись в базе данных."""
        form_data = {
            'text': 'Текстовый пост для создания второго поста',
            'group': PostCreateFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                    'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text='Текстовый пост для создания второго поста',
                group='1'
            ).exists()
        )
        self.assertRedirects(response,
                             reverse('posts:post_detail', kwargs={
                                 'post_id': f'{self.post.id}'
                             }))


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.c_user = User.objects.create_user(username='comment')
        cls.c_post = Post.objects.create(
            author=cls.c_user,
            text='Это тестовый текст длинною больше 15 символов.',
        )
        cls.comment_form = CommentForm()

    def setUp(self):
        cache.clear()
        self.authorized_c_client = Client()
        self.authorized_c_client.force_login(self.c_user)

    def test_comments(self):
        """Комментарии доступны только авторизованному пользователю
        после успешной отправки комментарий появляется на странице поста.
        """
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.authorized_c_client.post(
            reverse('posts:add_comment', kwargs={
                    'post_id': f'{self.c_post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый комментарий',
            ).exists()
        )
        self.assertRedirects(response,
                             reverse('posts:post_detail', kwargs={
                                 'post_id': f'{self.c_post.id}'
                             }))
