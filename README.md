# Foodgram

## Описание проекта

**Foodgram** - это веб-приложение, где пользователи могут публиковать рецепты, подписываться на любимых авторов, добавлять рецепты в избранное и формировать список покупок для выбранных рецептов.


## Технологии

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

## Возможности проекта

- Публикация своих рецептов с указанием ингредиентов иописанием приготовления;
- Просмотр рецептов других пользователей с возможностью фильтрации по тегам;
- Добавление рецептов в избранное для быстрого доступа;
- Подписка на авторов и просмотр их новых рецептов в ленте подписок;
- Формирование и скачивание списка покупок, основанного на выбранных рецептах;
- Смена пароля и редактирование профиля.

## Ресурсы API

1. Пользователи:
   - `GET /api/users/` - Список пользователей
   - `POST /api/users/` - Регистрация пользователя
   - `GET /api/users/{id}/` - Профиль пользователя
   - `GET /api/users/me/` - Текущий пользователь
   - `PUT /api/users/me/avatar/` - Добавление аватара
   - `DELETE /api/users/me/avatar/` - Удаление аватара
   - `POST /api/users/set_password/` - Изменение пароля

2. Теги:
   - `GET /api/tags/` - Список тегов
   - `GET /api/tags/{id}/` - Получение тега

3. Рецепты:
   - `GET /api/recipes/` - Список рецептов
   - `POST /api/recipes/` - Создание рецепта
   - `GET /api/recipes/{id}/` - Получение рецепта
   - `PATCH /api/recipes/{id}/` - Обновление рецепта
   - `DELETE /api/recipes/{id}/` - Удаление рецепта
   - `GET /api/recipes/{id}/get-link/` - Получить короткую ссылку на рецепт

4. Избранное:
   - `POST /api/recipes/{id}/favorite/` - Добавить рецепт в избранное
   - `DELETE /api/recipes/{id}/favorite/` - Удалить рецепт из избранного

5. Список покупок:
   - `POST /api/recipes/{id}/shopping_cart/` - Добавить рецепт в список покупок
   - `DELETE /api/recipes/{id}/shopping_cart/` - Удалить рецепт из списка покупок
   - `GET /api/recipes/download_shopping_cart/` - Скачать список покупок

6. Подписки:
   - `GET /api/users/subscriptions/` - Мои подписки
   - `POST /api/users/{id}/subscribe/` - Подписаться на пользователя
   - `DELETE /api/users/{id}/subscribe/` - Отписаться от пользователя

7. Ингредиенты:
   - `GET /api/ingredients/` - Список ингредиентов
   - `GET /api/ingredients/{id}/` - Получение ингредиента

8. Аутентификация:
   - `POST /api/auth/token/login/` - Получить токен авторизации
   - `POST /api/auth/token/logout/` - Удаление токена

## Примеры запросов к API:

### Регистрация нового пользователя:

Права доступа: **Доступно без токена**

```http request
POST http://127.0.0.1:8080/api/users/
Content-Type: application/json

{
    "email": "email@email.ru",
    "username": "username",
    "first_name": "Вася",
    "last_name": "Иванов",
    "password": "password"
}
```

### Получение токена:

Права доступа: **Доступно без токена**

```http request
POST http://127.0.0.1:8080/api/auth/token/login/
Content-Type: application/json

{
    "email": "email@email.ru",
    "password": "password"
}
```

### Выполнить логаут:

Права доступа: **Аутентифицированные пользователи**

```http request
POST http://127.0.0.1:8080/api/auth/token/logout/
Authorization: Token <токен текущего пользователя>
```

### Получить список пользователей:

Права доступа: **Доступно без токена**

```http request
### Получить весь список
GET http://127.0.0.1:8080/api/users/

### С указанием лимита
GET http://127.0.0.1:8080/api/users/?limit=1
```

### Получить профиль пользователя:

Права доступа: **Доступно без токена**

```http request
GET http://127.0.0.1:8080/api/users/{{userId}}/
```

### Получить свой профиль:

Права доступа: **Аутентифицированные пользователи**

```http request
GET http://127.0.0.1:8080/api/users/me/
Authorization: Token <токен текущего пользователя>
```

### Получить список тэгов:

Права доступа: **Доступно без токена**

```http request
GET http://127.0.0.1:8080/api/tags/
```

### Получить список тэгов:

Права доступа: **Доступно без токена**

```http request
GET http://127.0.0.1:8080/api/tags/
```

### Получить список ингредиентов:

Права доступа: **Доступно без токена**

```http request
### Получить список
GET http://127.0.0.1:8080/api/ingredients/

### Фильтр по имени
GET http://127.0.0.1:8080/api/ingredients/?name={{ingredientNameFirstLatter}}

### По ID
GET http://127.0.0.1:8080/api/ingredients/{{IndredientId}}/
```

### Создание рецепта:

Права доступа: **Аутентифицированные пользователи**

```http request
POST http://127.0.0.1:8080/api/recipes/
Authorization: Token <токен текущего пользователя>
Content-Type: application/json

{
  "ingredients": [
    {
      "id": "firstIndredientId",
      "amount": "firstIngredientAmount"
    },
    {
      "id": "secondIndredientId",
      "amount": "secondIngredientAmount"
    }
  ],
  "tags": [
    "firstTagId",
    "secondTagId"
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "Нечто съедобное (это не точно)",
  "text": "Приготовьте как нибудь эти ингредиеты",
  "cooking_time": 5
}
```

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
