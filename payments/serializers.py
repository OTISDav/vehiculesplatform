from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    #-----Historique des paiements du client connecte
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_payment_type_display', read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id', 'invoice_number',
            'payment_type', 'type_display',
            'amount', 'currency',
            'method', 'method_display',
            'status', 'status_display',
            'transaction_id',
            'created_at'
        )
        read_only_fields = fields


class PaymentInitSerializer(serializers.Serializer):
    #----Initialisation d'un paiement.Le frontend envoie ces donnees pour demarrer une transaction.

    METHOD_CHOICES = [
        ('stripe', 'Carte bancaire'),
        ('tmoney', 'TMoney'),
        ('flooz', 'Flooz'),
        ('cash_office', 'Au bureau'),
    ]
    TYPE_CHOICES = [
        ('rental', 'Réservation location'),
        ('part_order', 'Commande pièce'),
        ('transport_advance', 'Avance transport'),
    ]

    payment_type = serializers.ChoiceField(choices=TYPE_CHOICES)
    reference_id = serializers.IntegerField(
        help_text="ID de la réservation ou de la commande concernée"
    )
    method = serializers.ChoiceField(choices=METHOD_CHOICES)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    #------Pour les invites (commandes pieces sans compte)
    client_name = serializers.CharField(required=False, allow_blank=True)
    client_email = serializers.EmailField(required=False, allow_blank=True)

    def validate(self, attrs):
        request = self.context.get('request')
        if request and not request.user.is_authenticated:
            if not attrs.get('client_name'):
                raise serializers.ValidationError({"client_name": "Votre nom est requis."})
            if not attrs.get('client_email'):
                raise serializers.ValidationError({"client_email": "Votre email est requis."})
        return attrs


class StripePaymentIntentSerializer(serializers.Serializer):
    #-----Reponse renvoyee au frontend apres creation d'un PaymentIntent Stripe
    client_secret = serializers.CharField(read_only=True)
    payment_id = serializers.IntegerField(read_only=True)
    invoice_number = serializers.CharField(read_only=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)


class MobileMoneySerializer(serializers.Serializer):
    #----Initialisation d'un paiement mobile money (TMoney / Flooz)
    METHOD_CHOICES = [
        ('tmoney', 'TMoney'),
        ('flooz', 'Flooz'),
    ]

    method = serializers.ChoiceField(choices=METHOD_CHOICES)
    phone_number = serializers.CharField(
        max_length=20,
        help_text="Numéro de téléphone associé au compte mobile money"
    )
    payment_type = serializers.ChoiceField(choices=[
        ('rental', 'Réservation location'),
        ('part_order', 'Commande pièce'),
        ('transport_advance', 'Avance transport'),
    ])
    reference_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    client_name = serializers.CharField(required=False, allow_blank=True)
    client_email = serializers.EmailField(required=False, allow_blank=True)

    def validate_phone_number(self, value):
        cleaned = ''.join(c for c in value if c.isdigit() or c == '+')
        if len(cleaned) < 8:
            raise serializers.ValidationError("Numéro de téléphone invalide.")
        return cleaned