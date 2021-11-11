# Foodgram
http://84.201.160.204//signin

### Установка  
1. Клонироать репозиторий 
2. Установить на сервер Docker 
3. Настроить infa/nginx.conf
4. Скопируйте файлы docker-compose.yml и nginx.conf из директории infra на сервер
5. Создать на сервере файл .env и заполнить его:
```
DB_ENGINE=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
SECRET_KEY=
```
6. На сервере выполнить команду docker-compose up --build
7. Сделать миграции:
sudo docker-compose exec -T bacend python manage.py makemigrations
sudo docker-compose exec -T bacend python manage.py migrate

Ссылка на поект:  http://51.250.20.102/
email: admin@mail.ru passwoer: admin

###Технологи:
Docker
django
django REST framework
djoser
nginx


