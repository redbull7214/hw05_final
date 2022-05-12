from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Представление об авторе."""

    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Представление технологии."""

    template_name = 'about/tech.html'
