from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import KYCDocument
from .serializers import (
    RegisterSerializer, UserProfileSerializer,
    KYCSubmitSerializer, KYCStatusSerializer
)


class RegisterView(generics.CreateAPIView):
    #-----POST /api/v1/accounts/register/ — Inscription client
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    #-----GET/PUT /api/v1/accounts/profile/ — Profil du client connecte
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class KYCSubmitView(generics.CreateAPIView):
    #----POST /api/v1/accounts/kyc/submit/ — Soumettre dossier KYC
    serializer_class = KYCSubmitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Votre dossier KYC a été soumis. Vous serez notifié après vérification."},
            status=status.HTTP_201_CREATED
        )


class KYCStatusView(generics.RetrieveAPIView):
    #----GET /api/v1/accounts/kyc/status/ — Statut KYC du client
    serializer_class = KYCStatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.kyc
        except KYCDocument.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Aucun dossier KYC soumis.")

