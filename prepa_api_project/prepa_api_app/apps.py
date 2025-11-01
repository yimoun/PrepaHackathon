from django.apps import AppConfig


class PrepaApiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prepa_api_app'


# # créer le virtualenv si absent
# python3 -m venv venv

# # activer (macOS / zsh / bash)
# source venv/bin/activate

# # installer les dépendances du projet
# pip install --upgrade pip
# pip install -r requirements.txt

# # appliquer les migrations
# python manage.py migrate

# # (optionnel) créer un superuser
# python manage.py createsuperuser

# # lancer le serveur (localhost:8000)
# python manage.py runserver

# # ou accessible sur le réseau local
# python manage.py runserver 0.0.0.0:8000