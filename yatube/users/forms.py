from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    """Создание формы регистрации."""

    class Meta(UserCreationForm.Meta):
        """Определение полей формы."""

        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
