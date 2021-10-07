# Foodgram
http://84.201.160.204//signin

### Установка  
Установить Докер
выполнить команду:
docker pull Rigotka/foodgram :latest
выполнить миграции и собрать статику:
- docker-compose exec backend python manage.py migrate --noinput
- docker-compose exec backend python manage.py collectstatic --no-input

email: hz@mail.ru passwoer: hz
