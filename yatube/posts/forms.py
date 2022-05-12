from django import forms
from .models import Post, Comment
from django.utils.translation import gettext_lazy as _


class PostForm(forms.ModelForm):
    """Создание формы Post."""

    class Meta:
        """Описание полей формы."""

        model = Post
        fields = ('group', 'text', 'image')
        labels = {
            'text': _('Текст'),
            'group': _('Группа'),
            'image': _('Картинка'),
        }
        help_texts = {
            'text': _('Введите текст поста, длинна не менее 20 символов.'),
            'group': _('Выберите группу, к которой будет относиться пост.'),
            'image': _('Картинка в посте, необязательный атрибут.'),
        }

    def clean_text(self):
        """Фильтр на минимальную длинну поста."""
        data = self.cleaned_data['text']
        if len(data) < 20:
            raise forms.ValidationError('Минимум 20 символов')
        return data


class CommentForm(forms.ModelForm):
    """Создание формы комментариев."""

    class Meta:
        """Описание полей формы."""

        model = Comment
        fields = ('text',)
        labels = {'text': _('Текст'), }
        help_texts = {'text': _('Введите текст комментария.'), }
