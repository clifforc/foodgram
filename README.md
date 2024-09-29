# Foodgram

## Описание проекта

**Foodgram** - это веб-приложение, где пользователи могут публиковать рецепты, подписываться на любимых авторов, добавлять рецепты в избранное и формировать список покупок для выбранных рецептов.

## Возможности проекта

- Публикация своих рецептов с указанием ингредиентов иописанием приготовления;
- Просмотр рецептов других пользователей с возможностью фильтрации по тегам;
- Добавление рецептов в избранное для быстрого доступа;
- Подписка на авторов и просмотр их новых рецептов в ленте подписок;
- Формирование и скачивание списка покупок, основанного на выбранных рецептах;
- Смена пароля и редактирование профиля.

## Технологии

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
- Python
- Django
- Django REST
- Djoser
- PostgreSQL
- Docker
- Docker Compose
- Nginx
- Gunicorn
- GitHub Actions (CI/CD)

## Установка и запуск проекта

### Клонирование репозитория

```bash
git clone https://github.com/clifforc/foodgram.git
```

### Настройка переменных окружения

В корневой директории создайте файл `.env` с содержимым:

```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram
POSTGRES_PASSWORD=foodgram_pwd
DB_NAME=foodgram

DB_HOST=db
DB_PORT=5432
```

### Запуск приложения в Docker

Перейдите в директорию `infra/` и выполните команду:

```bash
docker compose up -d --build
```

### Доступ к приложению

Приложение будет доступно по адресу: `http://localhost:8080/`
