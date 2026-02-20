from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import TransportRequestSerializer


class TransportRequestCreateView(generics.CreateAPIView):
    #-----POST /api/v1/logistics/transport/ — Demander un devis de transport
    serializer_class = TransportRequestSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transport = serializer.save()
        return Response(
            {
                "message": "Votre demande de devis a été enregistrée. Nous vous contacterons sous 24h.",
                "id": transport.id,
                "customs_note": transport.customs_note,
            },
            status=status.HTTP_201_CREATED
        )