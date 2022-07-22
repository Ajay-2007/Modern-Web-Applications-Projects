docker run --name django_chat_dev_redis -d -p 6379:6379 redis
python manage.py collectstatic
python manage.py startapp account
python manage.py makemigrations
python manage.py migrate