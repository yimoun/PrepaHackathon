from django.contrib.auth.models import User, update_last_login
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer  #Gère l’authentification avec JWT.
from rest_framework_simplejwt.settings import api_settings  #Accède aux paramètres de Django REST Framework JWT.


#Le TokenSerializer joue un rôle clé dans l’authentification JWT: Son rôle principale est de générer un jeton
#JWT(JSON Web Token) pour l'authentification des utilisateus dans l'API Django et de permettre au projet React
#d'utiliser ces jetons pour interagir avec l'API de manière sécurisée. Il génère "access" et "refresh"
# lorsque l’utilisateur se connecte.
#Le front-end React utilise access pour accéder aux routes protégées de l'API
#Quand access expire, refresh permet d’obtenir un nouveau access sans devoir se reconnecter.


#Ce sérializer permet d'afficher les informations d’un utilisateur (GET).
class UserSerializer(ModelSerializer):
    class Meta:
        model = User  #Utilise le modèle utilisateur Django.
        fields = ["first_name", "last_name", "email", "username"]


#Ce sérializer est utilisé pour modifier le mot de passe (PUT ou PATCH).
class UserPasswordSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['password']

    def update(self, user, validated_data):
        user.set_password(validated_data.get('password', user.password))  #Chiffre le nouveau mot de passe avant de l’enregistrer.
        user.save()
        return user

#Ce sérializer permet de créer un nouvel utilisateur (POST).
class RegisterSerializer(ModelSerializer):
  class Meta:
    model = User
    fields = ["first_name", "last_name", "email", "username", "password"]

  def create(self, validated_data):
    user = User.objects.create_user(**validated_data) #Crée un nouvel utilisateur avec un mot de passe haché.
    return user


#Ce sérializer génère un token JWT (access + refresh) pour l’authentification.
class TokenSerializer(TokenObtainPairSerializer):
  def validate(self, attrs):  #Surcharge la méthode validate() pour personnaliser la réponse.
    data = super().validate(attrs)  #Appelle la validation par défaut de Django REST Framework.

    refresh = self.get_token(self.user) #Génère un token JWT.

    data['access'] = str(refresh.access_token)  #Retourne le token d’accès JWT (utilisé pour s’authentifier).
    data['refresh'] = str(refresh)  #Retourne le token de rafraîchissement (permet de générer un nouveau access).
    #Ajoute les informations utilisateur à la réponse.
    data['user'] = UserSerializer(self.user, context={'request': self.context['request']}).data

    if api_settings.UPDATE_LAST_LOGIN:  #Met à jour "last_login" si l'option est activée.
      update_last_login(None, self.user)

    return data
