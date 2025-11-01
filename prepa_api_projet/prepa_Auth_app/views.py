# Create your views here.
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed  #Gère les erreurs d’authentification.
from rest_framework.response import Response  #Formatage des réponses API.
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .utils import verify_recaptcha


from .Serializers import \
  UserSerializer, \
  UserPasswordSerializer, \
  RegisterSerializer, \
  TokenSerializer


#Cette view permet d’obtenir (GET) ou modifier (PUT) les informations d’un utilisateur.
class CurrentUserView(APIView):
  http_method_names = ['get', 'put']
  permission_classes = [IsAuthenticated]

  def get(self, request):
    user = User.objects.get(pk=request.user.pk)
    user_serializer = UserSerializer(user, context={'request': request})
    return Response(user_serializer.data, status=status.HTTP_200_OK)

  def put(self, request): #Modifie le nom d’utilisateur et l’email si disponibles.
    username = request.data['username']
    existing_user = User.objects.exclude(pk=request.user.pk).filter(username=username).first()
    if existing_user is not None:
      return Response('username_already_exists', status=status.HTTP_400_BAD_REQUEST)

    email = request.data['email']
    existing_user = User.objects.exclude(pk=request.user.pk).filter(email=email).first()
    if existing_user is not None:
      return Response('email_already_exists', status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.get(pk=request.user.pk)
    serializer = UserSerializer(user, data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    updated_user = serializer.save()

    user_serializer = UserSerializer(updated_user, context={'request': request})
    return Response(user_serializer.data, status=status.HTTP_200_OK)


#Cette View permet à l’utilisateur de changer son mot de passe (PUT).
class CurrentUserPasswordView(APIView):
  http_method_names = ['put']
  permission_classes = [IsAuthenticated]  #Accessible uniquement aux utilisateurs authentifiés

  def put(self, request):
    user = User.objects.get(pk=request.user.pk)
    serializer = UserPasswordSerializer(user, data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    updated_user = serializer.save() # est ce que c'est pas update à la place de save ?

    user_serializer = UserSerializer(updated_user, context={'request': request})
    return Response(user_serializer.data, status=status.HTTP_200_OK)


#Cette View permet à un utilisateur de créer un compte (POST).
class RegisterView(APIView):
  http_method_names = ['post']

  def post(self, request):
    #recaptcha_token = request.data.get("recaptcha_token")
    #if not verify_recaptcha(recaptcha_token):
        #return Response({"error": "reCAPTCHA invalide"}, status=status.HTTP_400_BAD_REQUEST)

    username = request.data['username']
    existing_user = User.objects.filter(username=username).first()
    if existing_user is not None:
      return Response('username_already_exists', status=status.HTTP_400_BAD_REQUEST)

    email = request.data['email']
    existing_user = User.objects.filter(email=email).first()
    if existing_user is not None:
      return Response('email_already_exists', status=status.HTTP_400_BAD_REQUEST)

    serializer = RegisterSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    created_user = serializer.save()

    user_serializer = UserSerializer(created_user, context={'request': request})
    return Response(user_serializer.data, status=status.HTTP_201_CREATED)


#Cette View permet aux utilisateurs de se connecter et de recevoir des tokens ("access" et "refresh") JWT
class TokenViewSet(ViewSet, TokenObtainPairView):
  http_method_names = ['post']
  permission_classes = (AllowAny,)
  serializer_class = TokenSerializer #C'est ce serailizer qui permet de générer les token

  def create(self, request):
    recaptcha_token = request.data.get("recaptcha_token")
    if not verify_recaptcha(recaptcha_token):
        return Response({"error": "reCAPTCHA invalide"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = self.get_serializer(data=request.data, context={'request': request})

    try:
      serializer.is_valid(raise_exception=True)
    except AuthenticationFailed:
      return Response('no_active_account', status=status.HTTP_401_UNAUTHORIZED)
    except TokenError as e:
      raise InvalidToken(e.args[0])

    return Response(serializer.validated_data, status=status.HTTP_200_OK)


#Cette View permet d’obtenir un nouveau access (lorsque l’ancien a expiré) en envoyant le refresh (sans devoir se connecter).
class TokenRefreshViewSet(ViewSet, TokenRefreshView):
  http_method_names = ['post']
  permission_classes = (AllowAny,)

  def create(self, request):
    serializer = self.get_serializer(data=request.data, context={'request': request})

    try:
      serializer.is_valid(raise_exception=True)
    except TokenError as e:
      raise InvalidToken(e.args[0])

    return Response(serializer.validated_data, status=status.HTTP_200_OK)


#Cette View permet de supprime l’utilisateur authentifié et renvoie une réponse HTTP 204 (No Content).
class CurrentUserDeleteView(APIView):
    http_method_names = ['delete']
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user  # Récupère l'utilisateur authentifié
        user.delete()  # Supprime l'utilisateur
        return Response({"message": "Compte supprimé avec succès"}, status=status.HTTP_204_NO_CONTENT)