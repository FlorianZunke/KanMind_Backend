from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from .serializers import RegistrationSerializer, EmailLoginSerializer

class RegistrationView(APIView):
    """
    POST /registration/
    → Register a new user account.

    Handles incoming registration data, validates via RegistrationSerializer,
    creates the user, generates an auth token, and returns user details plus token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Accepts JSON with 'fullname', 'email', 'password', and 'repeated_password'.
        - Validates input against RegistrationSerializer.
        - On success: creates User, issues Token, returns 201 Created with:
            {
              'user_id': int,
              'token': str,
              'fullname': str,
              'email': str
            }
        - On failure: returns 400 Bad Request with serializer errors.
        """
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'user_id': saved_account.id,
                'token': token.key,
                'fullname': saved_account.username,
                'email': saved_account.email,
            }
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CustomLoginView(ObtainAuthToken):
    """
    POST /login/
    → Authenticate a user via email and password.

    Uses EmailLoginSerializer to validate credentials, then returns an auth token
    and basic user info on successful login.
    """
    permission_classes = [AllowAny]
    serializer_class = EmailLoginSerializer

    def post(self, request):
        """
        Accepts JSON with 'email' and 'password'.
        - Validates credentials; on success, issues/retrieves Token.
        - Returns 200 OK with:
            {
              'token': str,
              'user_id': int,
              'fullname': str,
              'email': str
            }
        - On failure: returns 400 Bad Request with serializer errors.
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'user_id': user.id,
                'fullname': user.username,
                'email': user.email,
            }
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)