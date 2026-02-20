import stripe
import logging
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Payment
from .serializers import (
    PaymentSerializer,
    PaymentInitSerializer,
    MobileMoneySerializer,
)

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)



def get_related_objects(payment_type, reference_id):

    #----Retourne l'objet (Rental ou SparePartOrder) correspondant au paiement, selon son type.

    if payment_type == 'rental':
        from orders.models import Rental
        return Rental.objects.filter(pk=reference_id).first()
    elif payment_type == 'part_order':
        from orders.models import SparePartOrder
        return SparePartOrder.objects.filter(pk=reference_id).first()
    return None


def build_payment_record(request, validated_data, method, transaction_id=''):
    #----Cree un enregistrement Payment en base
    return Payment.objects.create(
        client=request.user if request.user.is_authenticated else None,
        client_name=validated_data.get('client_name', ''),
        client_email=validated_data.get('client_email', ''),
        payment_type=validated_data['payment_type'],
        rental_id=validated_data['reference_id'] if validated_data['payment_type'] == 'rental' else None,
        order_id=validated_data['reference_id'] if validated_data['payment_type'] == 'part_order' else None,
        amount=validated_data['amount'],
        currency='XOF',
        method=method,
        transaction_id=transaction_id,
        status='pending',
    )



class PaymentHistoryView(generics.ListAPIView):

    #-----GET /api/v1/payments/ Retourne l'historique des paiements du client connecte

    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(client=self.request.user).order_by('-created_at')



class PaymentDetailView(generics.RetrieveAPIView):

    #----GET /api/v1/payments/<id>/ Detail d'un paiement specifique.

    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(client=self.request.user)



class StripePaymentIntentView(APIView):

    #----POST /api/v1/payments/stripe/init/ Cree un PaymentIntent Stripe et retourne le client_secret au frontend pour finaliser le paiement côté client.

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PaymentInitSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        related = get_related_objects(data['payment_type'], data['reference_id'])
        if not related:
            return Response(
                {"error": "Réservation ou commande introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            #----Stripe travaille en centimes — on convertit FCFA → centimes EUR (approx)
            #----En production, utilisez un taux de change ou une devise supportée
            #----XOF n'est pas supporté nativement par Stripe, on utilise EUR comme proxy
            amount_in_cents = int(data['amount'] * 100 / 655)  # 1 EUR ≈ 655 FCFA

            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency='eur',
                metadata={
                    'payment_type': data['payment_type'],
                    'reference_id': data['reference_id'],
                    'platform': 'vehicules_togo',
                }
            )

            # Créer le paiement en base (statut pending)
            payment = build_payment_record(
                request, data,
                method='stripe',
                transaction_id=intent['id']
            )

            return Response({
                'client_secret': intent['client_secret'],
                'payment_id': payment.id,
                'invoice_number': payment.invoice_number,
                'amount': data['amount'],
            }, status=status.HTTP_201_CREATED)

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return Response(
                {"error": "Erreur lors de la création du paiement. Veuillez réessayer."},
                status=status.HTTP_502_BAD_GATEWAY
            )


# ─── Vue 4 : Webhook Stripe (confirmation automatique) ───────────────────────

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    POST /api/v1/payments/stripe/webhook/

    Stripe appelle cet endpoint automatiquement quand un paiement
    est confirmé, échoué ou remboursé.
    NE PAS protéger avec JWT — Stripe envoie sa propre signature.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response({"error": "Payload invalide."}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response({"error": "Signature invalide."}, status=status.HTTP_400_BAD_REQUEST)

        # Paiement réussi
        if event['type'] == 'payment_intent.succeeded':
            intent = event['data']['object']
            self._handle_payment_success(intent)

        # Paiement échoué
        elif event['type'] == 'payment_intent.payment_failed':
            intent = event['data']['object']
            self._handle_payment_failure(intent)

        return Response({"status": "ok"})

    def _handle_payment_success(self, intent):
        """Marque le paiement comme complété et met à jour la réservation/commande."""
        try:
            payment = Payment.objects.get(transaction_id=intent['id'])
            payment.status = 'completed'
            payment.save()

            # Mettre à jour le statut de la réservation ou commande liée
            if payment.payment_type == 'rental' and payment.rental_id:
                from orders.models import Rental
                rental = Rental.objects.get(pk=payment.rental_id)
                rental.amount_paid += payment.amount
                if rental.amount_paid >= rental.total_price:
                    rental.status = 'confirmed'
                rental.save()

            elif payment.payment_type == 'part_order' and payment.order_id:
                from orders.models import SparePartOrder
                order = SparePartOrder.objects.get(pk=payment.order_id)
                order.status = 'confirmed'
                order.save()

            logger.info(f"Paiement {payment.invoice_number} confirmé via Stripe.")

        except Payment.DoesNotExist:
            logger.warning(f"Paiement introuvable pour transaction Stripe {intent['id']}")

    def _handle_payment_failure(self, intent):
        """Marque le paiement comme échoué."""
        try:
            payment = Payment.objects.get(transaction_id=intent['id'])
            payment.status = 'failed'
            payment.save()
            logger.warning(f"Paiement {payment.invoice_number} échoué.")
        except Payment.DoesNotExist:
            pass


# ─── Vue 5 : Paiement Mobile Money (TMoney / Flooz) ──────────────────────────

class MobileMoneyPaymentView(APIView):
    """
    POST /api/v1/payments/mobile-money/

    Initie un paiement via TMoney ou Flooz.

    Note : TMoney et Flooz n'ont pas d'API publique documentée universelle.
    Ce code suit le pattern standard d'intégration mobile money en Afrique
    (push USSD / API REST opérateur). À adapter selon l'API réelle fournie
    par l'opérateur Togocom / Moov.

    Corps de la requête :
    {
        "method": "tmoney",            // ou "flooz"
        "phone_number": "+22890000000",
        "payment_type": "part_order",
        "reference_id": 5,
        "amount": 25000
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = MobileMoneySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Vérifier que l'objet lié existe
        related = get_related_objects(data['payment_type'], data['reference_id'])
        if not related:
            return Response(
                {"error": "Réservation ou commande introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Créer le paiement en base (statut pending)
        payment = build_payment_record(
            request, data,
            method=data['method'],
            transaction_id=''  # sera rempli après confirmation opérateur
        )

        # ── Appel API opérateur (à implémenter selon doc officielle) ──────────
        # Exemple générique — à remplacer par l'API réelle Togocom/Moov
        try:
            operator_response = self._call_operator_api(
                method=data['method'],
                phone=data['phone_number'],
                amount=data['amount'],
                reference=payment.invoice_number,
            )

            if operator_response.get('success'):
                payment.transaction_id = operator_response.get('transaction_id', '')
                payment.status = 'pending'  # En attente confirmation USSD client
                payment.save()

                return Response({
                    'message': f"Une demande de paiement {data['method'].upper()} a été envoyée au {data['phone_number']}. Veuillez confirmer sur votre téléphone.",
                    'payment_id': payment.id,
                    'invoice_number': payment.invoice_number,
                    'amount': str(data['amount']),
                    'method': data['method'],
                }, status=status.HTTP_201_CREATED)

            else:
                payment.status = 'failed'
                payment.save()
                return Response(
                    {"error": operator_response.get('message', "Échec de l'initiation du paiement.")},
                    status=status.HTTP_502_BAD_GATEWAY
                )

        except Exception as e:
            logger.error(f"Erreur mobile money ({data['method']}): {e}")
            payment.status = 'failed'
            payment.save()
            return Response(
                {"error": "Erreur de connexion avec l'opérateur. Veuillez réessayer."},
                status=status.HTTP_502_BAD_GATEWAY
            )

    def _call_operator_api(self, method, phone, amount, reference):
        """
        Méthode à implémenter selon la documentation officielle
        de l'opérateur (Togocom pour TMoney, Moov pour Flooz).

        Retourne un dict : {'success': bool, 'transaction_id': str, 'message': str}
        """
        # TODO: Remplacer par l'intégration réelle
        # Exemple de structure d'appel :
        # import requests
        # if method == 'tmoney':
        #     url = "https://api.togocom.tg/payment/push"
        #     headers = {"Authorization": f"Bearer {settings.TMONEY_API_KEY}"}
        #     payload = {"phone": phone, "amount": amount, "ref": reference}
        #     resp = requests.post(url, json=payload, headers=headers)
        #     return resp.json()

        raise NotImplementedError(
            "L'intégration TMoney/Flooz doit être implémentée "
            "selon la documentation officielle de l'opérateur."
        )


# ─── Vue 6 : Confirmer un paiement mobile money (callback opérateur) ─────────

class MobileMoneyCallbackView(APIView):
    """
    POST /api/v1/payments/mobile-money/callback/

    L'opérateur (Togocom/Moov) appelle cet endpoint pour confirmer
    ou rejeter un paiement mobile money.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # Structure du callback à adapter selon l'opérateur
        invoice_number = request.data.get('reference')
        transaction_id = request.data.get('transaction_id')
        callback_status = request.data.get('status')  # 'success' ou 'failed'

        if not invoice_number:
            return Response({"error": "Référence manquante."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(invoice_number=invoice_number)

            if callback_status == 'success':
                payment.status = 'completed'
                payment.transaction_id = transaction_id or payment.transaction_id
                payment.save()

                # Mettre à jour la réservation/commande liée
                if payment.payment_type == 'rental' and payment.rental_id:
                    from orders.models import Rental
                    rental = Rental.objects.get(pk=payment.rental_id)
                    rental.amount_paid += payment.amount
                    if rental.amount_paid >= rental.total_price:
                        rental.status = 'confirmed'
                    rental.save()

                elif payment.payment_type == 'part_order' and payment.order_id:
                    from orders.models import SparePartOrder
                    order = SparePartOrder.objects.get(pk=payment.order_id)
                    order.status = 'confirmed'
                    order.save()

                logger.info(f"Mobile money confirmé : {payment.invoice_number}")
                return Response({"status": "ok"})

            else:
                payment.status = 'failed'
                payment.save()
                logger.warning(f"Mobile money échoué : {payment.invoice_number}")
                return Response({"status": "failed"})

        except Payment.DoesNotExist:
            return Response({"error": "Paiement introuvable."}, status=status.HTTP_404_NOT_FOUND)


# ─── Vue 7 : Vérifier le statut d'un paiement ────────────────────────────────

class PaymentStatusView(APIView):
    """
    GET /api/v1/payments/<invoice_number>/status/
    Permet au frontend de vérifier si un paiement a été confirmé.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, invoice_number, *args, **kwargs):
        try:
            payment = Payment.objects.get(invoice_number=invoice_number)
            return Response({
                'invoice_number': payment.invoice_number,
                'status': payment.status,
                'status_display': payment.get_status_display(),
                'amount': str(payment.amount),
                'method': payment.get_method_display(),
            })
        except Payment.DoesNotExist:
            return Response({"error": "Paiement introuvable."}, status=status.HTTP_404_NOT_FOUND)