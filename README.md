# Foodgram
http://84.252.137.68/signin

### Установка  
Установить Докер
выполнить команду:
docker pull Rigotka/foodgram :latest
выполнить миграции и собрать статику:
- docker-compose exec backend python manage.py migrate --noinput
- docker-compose exec backend python manage.py collectstatic --no-input

email: hz@mail.ru passwoer: hz
