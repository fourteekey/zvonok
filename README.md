### Установка проекта
```
$ pip install -r requirements
$ cd backend
$ cp config/example.env config/.env
$ nano config/.env
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py insert_archive_status
$ python manage.py createsuperuser
 ```


### Запуск бэкенда
``
$ docker-compose build
$ docker-compose up
``
