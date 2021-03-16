[![yamdb_final](https://github.com/Antosh2020/yamdb_final/workflows/yamdb_workflow/badge.svg?branch=master)](https://github.com/Antosh2020/yamdb_final/actions)

# YaMDb http://178.154.225.90:5000/redoc/

REST API for YaMDb, собирает отзывы пользователей на произведения.
Произведения делятся на категории: «Книги», «Фильмы», «Музыка».

Доступные запросы к API:
/api/v1/posts (GET, POST, PUT, PATCH, DELETE)
/api/v1/posts/<id> (GET, POST, PUT, PATCH, DELETE)
/api/v1/posts/<id>/comments (GET, POST, PUT, PATCH, DELETE)
/api/v1/posts/<id>/comments/<id> (GET, POST, PUT, PATCH, DELETE)
/api/v1/group/ (GET, POST)
/api/v1/follow/ (GET, POST)

## Getting Started

1. Устанавливаем Docker
2. Собираем docker-compose командой:
    docker-compose up -d --build
3. Создаем суперпользователя Django командой:
    docker-compose run web python manage.py createsuperuser
4. Наполняем базу данными командой:
    docker-compose exec web python3 manage.py loaddata fixture.json

### Технологии
Python
Django
Django REST framework

### Автор
Anton Levishko: https://github.com/Antosh2020


