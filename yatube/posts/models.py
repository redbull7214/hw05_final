from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    """Создание модели Post."""

    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        """Сортировка по дате поста."""

        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        """Метод __str__ возвращает первые 15 символов поста."""
        return self.text[:15]


class Group(models.Model):
    """Создание модели Group."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        """Метод __str__ возвращает название группы."""
        return self.title


class Comment(models.Model):
    """Создание модели Comment."""

    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        'Дата и время публикации',
        auto_now_add=True
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    def __str__(self):
        """Метод __str__ возвращает первые 15 символов комментария."""
        return self.text[:15]


class Follow(models.Model):
    """Создание модели Follow."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
