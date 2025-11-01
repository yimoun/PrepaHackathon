# PrepaHackathon
Ce repository contient tout ce que mon coéquipier et moi faisons pour préparer ce Hackathon

🏭 ConformAI Saguenay

Projet de simulation IA - Détection automatique d’EPI (casque et lunettes) dans une usine d’aluminium

📘 Présentation du projet

ConformAI Saguenay est une solution de vision artificielle destinée à améliorer la sécurité industrielle dans les usines du Saguenay (Alma / Jonquière).
Le système repose sur un modèle YOLOv8 préentraîné capable de détecter en temps réel si les employés portent leurs équipements de protection individuelle (EPI) — notamment le casque et les lunettes de sécurité.

🎯 Objectifs

Détection automatique du port de casque et lunettes à partir du flux caméra.

Génération d’alertes en cas de non-conformité.

Suivi et statistiques via un tableau de bord technique.

Exportation des rapports PDF d’incidents pour audit et conformité.


⚙️ Architecture technique

Frontend : React + Vite

Backend : Django + Django REST Framework

IA : YOLOv8 intégré côté serveur (backend Python)

Base de données : PostgreSQL (ou SQLite pour la démo)



🚀 Installation et lancement
🔹 Prérequis

    Python 3.10+

    Node.js 18+

    npm ou yarn

    pipenv ou venv recommandé pour Django

    PostgreSQL (optionnel pour la démo)


⚙️ 2. Lancer le backend (Django)
    python -m venv venv
    source venv/bin/activate      # macOS / Linux
    venv\Scripts\activate         # Windows
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver


💻 3. Lancer le frontend (React)
    npm install
    npm run dev ou npm start


📊 Fonctionnalités principales

✅ Détection automatique EPI (casque, lunettes)
✅ Tableau de bord des alertes
✅ Sélection du modèle IA et réglage de la sensibilité
✅ Export PDF des incidents
✅ Historique et statistiques
