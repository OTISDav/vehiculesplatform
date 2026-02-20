from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Rental, SparePartOrder, ContactMessage
from .serializers import (
    RentalCreateSerializer, RentalDetailSerializer,
    SparePartOrderCreateSerializer, SparePartOrderDetailSerializer,
    ContactMessageSerializer
)


class RentalCreateView(generics.CreateAPIView):
    #------POST /api/v1/orders/rentals/ — Creer une reservation de location
    serializer_class = RentalCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rental = serializer.save()
        return Response(
            RentalDetailSerializer(rental, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class RentalListView(generics.ListAPIView):
    #----GET /api/v1/orders/rentals/ — Reservations du client connecte
    serializer_class = RentalDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Rental.objects.filter(client=self.request.user).select_related('vehicle')


class RentalDetailView(generics.RetrieveAPIView):
    #----GET /api/v1/orders/rentals/<id>/ — Detail d'une reservation
    serializer_class = RentalDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Rental.objects.filter(client=self.request.user)


class SparePartOrderCreateView(generics.CreateAPIView):
    #---POST /api/v1/orders/parts/ — Commander une piece (avec ou sans compte)
    serializer_class = SparePartOrderCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            SparePartOrderDetailSerializer(order, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class SparePartOrderListView(generics.ListAPIView):
    #----GET /api/v1/orders/parts/ — Commandes du client connecte
    serializer_class = SparePartOrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SparePartOrder.objects.filter(client=self.request.user).select_related('part')


class SparePartOrderDetailView(generics.RetrieveAPIView):
    #-----GET /api/v1/orders/parts/<id>/ — Detail d'une commande de piece
    serializer_class = SparePartOrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SparePartOrder.objects.filter(client=self.request.user)


class ContactMessageCreateView(generics.CreateAPIView):
    #------POST /api/v1/orders/contact/ — Envoyer un message de contact
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Votre message a bien été envoyé. Nous vous répondrons rapidement."},
            status=status.HTTP_201_CREATED
        )

