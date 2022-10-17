hw05_final
# Финальная версия проекта Yatube
- Создана система подписок на авторов
- Добавлены кастомные страницы ошибок
- Добавлены картинки к постам
- Настроено кеширование
- Проведен рефакторинг

# Технологии
- Python 3.8
- Django 2.2.14
- mixer
- Pillow
- sorl-thumbnai

## _Как запустить проект:_
Клонировать репозиторий и перейти в него в командной строке
Cоздать и активировать виртуальное окружение:

```sh
python -m venv venv
source venv/Scripts/activate 
```
Установить зависимости из файла requirements.txt и обновить pip:
```sh
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Запустить сервер:
```sh

py manage.py runserver
```

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)
