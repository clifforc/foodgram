python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py run_import
gunicorn --bind 0:8000 foodgram.wsgi