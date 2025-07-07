from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import RegistrationSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'user_id': saved_account.id,
                'token': token.key,
                'fullname': saved_account.first_name + saved_account.last_name,
                'email': saved_account.email,
            }
        else:
            data = serializer.errors

        return Response(data)