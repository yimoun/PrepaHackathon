from django.urls import include, path
from rest_framework import routers  #Gère les routes automatiques pour les ViewSets.

from . import views


# Seulement pour modifier le nom du router (Api Root --> Api Auth)
class AuthRootView(routers.APIRootView):
    def get_view_name(self) -> str:
        return "Api Auth"


# Ici, on personnalise le APIRootView pour utiliser AuthRootView (défini ci-dessus).
class AuthRouter(routers.DefaultRouter):
    APIRootView = AuthRootView


# Create a router and register our viewsets with it.
router = AuthRouter()

# Appeler en POST
router.register(r'token', views.TokenViewSet, basename='token')  # Connexion et récupération des tokens(access et refresh).
router.register(r'token-refresh', views.TokenRefreshViewSet, basename='token-refresh')  # Rafraîchissement du access token avec refresh.
# Ces routes utilisent des ViewSets, ce qui signifie que Django génère automatiquement les endpoints
# pour ces actions contrairement au routes manuelles déclarées ci-dessous.


# Ces routes utilisent des APIView et nécessitent d’être déclarées manuellement.
urlpatterns = [
    path('', include(router.urls)),

    # Appeler en GET
    path('current-user/', views.CurrentUserView.as_view()),  # /api/auth/current-user/

    # Appeler en PUT
    path('current-user/me/', views.CurrentUserView.as_view()),  # /api/auth/current-user/me/
    path('current-user-password/me/', views.CurrentUserPasswordView.as_view()),  # /api/auth/current-user-password/me/

    # Appeler en POST
    path('register/', views.RegisterView.as_view()),  # /api/auth/resgister

    # Appeler en DELETE
    path('user-delete/me/', views.CurrentUserDeleteView.as_view()),  # /api/auth/user-delete/me/

]

# Ce fichier gère toutes les routes d'authentification et de gestion des utilisateurs
# Routes générées automatiquement (celles dont les view sont de type ViewSets) avec router :connexion JWT et rafraichissement JWT
# Routes définies manuellement (celles dont les views sont de type APIView)

# ces ligne sont inspirées du tp4_Auth_app de Nelson Yimbou.