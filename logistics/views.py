import io
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import TransportZone, TransportRequest
from .serializers import (
    TransportZoneSerializer,
    TransportRequestCreateSerializer,
    TransportRequestDetailSerializer,
    TransportEstimateSerializer,
)


class TransportZoneListView(generics.ListAPIView):
    """
    GET /api/v1/logistics/zones/
    Liste des zones tarifaires actives — visible par tous.
    """
    queryset = TransportZone.objects.filter(is_active=True)
    serializer_class = TransportZoneSerializer
    permission_classes = [permissions.AllowAny]


class TransportEstimateView(APIView):
    """
    POST /api/v1/logistics/estimate/
    Simulateur de coût sans créer de demande.

    Body: { "origin_country": "France", "vehicle_weight_kg": 1500 }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = TransportEstimateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.get_estimate()
        return Response(result)


class TransportRequestCreateView(generics.CreateAPIView):
    """
    POST /api/v1/logistics/requests/
    Créer une demande de transport.
    Détecte la zone automatiquement et calcule l'estimation.
    """
    serializer_class = TransportRequestCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transport = serializer.save()

        return Response(
            TransportRequestDetailSerializer(transport).data,
            status=status.HTTP_201_CREATED
        )


class TransportRequestDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/logistics/requests/<id>/
    Détail d'une demande avec toutes les étapes de suivi.
    """
    queryset = TransportRequest.objects.prefetch_related('steps').select_related('zone', 'transporter', 'vehicle')
    serializer_class = TransportRequestDetailSerializer
    permission_classes = [permissions.AllowAny]


class TransportRequestTrackView(APIView):
    """
    GET /api/v1/logistics/track/<id>/
    Suivi public simplifié — le client suit sa demande avec son ID.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, *args, **kwargs):
        try:
            transport = TransportRequest.objects.prefetch_related('steps').select_related(
                'zone', 'transporter', 'vehicle'
            ).get(pk=pk)
        except TransportRequest.DoesNotExist:
            return Response({"error": "Demande introuvable."}, status=status.HTTP_404_NOT_FOUND)

        steps = transport.steps.all().order_by('reached_at')
        all_statuses = TransportRequest.STATUS_CHOICES
        current_index = next(
            (i for i, (s, _) in enumerate(all_statuses) if s == transport.status), 0
        )

        return Response({
            'id': transport.id,
            'vehicle': transport.vehicle.title,
            'origin': f"{transport.origin_city or ''} {transport.origin_country}".strip(),
            'destination': transport.destination_city,
            'status': transport.status,
            'status_display': transport.get_status_display(),
            'estimated_cost': transport.estimated_cost,
            'final_cost': transport.final_cost,
            'advance_required': transport.advance_required,
            'advance_paid': transport.advance_paid,
            'delay': f"{transport.zone.delay_days_min}–{transport.zone.delay_days_max} jours" if transport.zone else "À confirmer",
            'customs_note': transport.customs_note,
            'client_note': transport.client_note,
            'transporter': transport.transporter.name if transport.transporter else None,
            'progress_percent': int((current_index / max(len(all_statuses) - 2, 1)) * 100),
            'steps': [
                {
                    'status': s.status,
                    'status_display': s.get_status_display(),
                    'title': s.title,
                    'description': s.description,
                    'location': s.location,
                    'reached_at': s.reached_at,
                    'is_current': s.status == transport.status,
                }
                for s in steps
            ],
            'created_at': transport.created_at,
        })


class TransportRequestPDFView(APIView):
    """
    GET /api/v1/logistics/requests/<id>/pdf/
    Génère et retourne une fiche récapitulative PDF.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, *args, **kwargs):
        try:
            transport = TransportRequest.objects.select_related(
                'zone', 'transporter', 'vehicle', 'vehicle__brand', 'vehicle__model'
            ).prefetch_related('steps').get(pk=pk)
        except TransportRequest.DoesNotExist:
            return Response({"error": "Demande introuvable."}, status=status.HTTP_404_NOT_FOUND)

        pdf_content = self._generate_pdf(transport)
        filename = f"transport_{transport.pk}_{transport.client_name.replace(' ', '_')}.pdf"

        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def _generate_pdf(self, transport):
        """
        Génère le PDF avec ReportLab.
        Installe avec : pip install reportlab
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                    topMargin=2*cm, bottomMargin=2*cm,
                                    leftMargin=2*cm, rightMargin=2*cm)

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('Title', parent=styles['Title'],
                                         fontSize=20, textColor=colors.HexColor('#1F4E79'),
                                         spaceAfter=6, alignment=TA_CENTER)
            subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
                                            fontSize=11, textColor=colors.HexColor('#2E75B6'),
                                            spaceAfter=4, alignment=TA_CENTER)
            section_style = ParagraphStyle('Section', parent=styles['Normal'],
                                           fontSize=12, textColor=colors.white,
                                           backColor=colors.HexColor('#1F4E79'),
                                           spaceAfter=2, spaceBefore=8,
                                           leftIndent=6)
            normal = styles['Normal']

            elements = []

            # ── En-tête ───────────────────────────────────────────────────────
            elements.append(Paragraph("FICHE RÉCAPITULATIVE DE TRANSPORT", title_style))
            elements.append(Paragraph("Plateforme Véhicules & Pièces — Lomé, Togo", subtitle_style))
            elements.append(Spacer(1, 0.3*cm))
            elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1F4E79')))
            elements.append(Spacer(1, 0.4*cm))

            # ── Référence ─────────────────────────────────────────────────────
            ref_data = [
                ['Référence dossier', f'TRANSPORT-{transport.pk:04d}'],
                ['Date de création', transport.created_at.strftime('%d/%m/%Y')],
                ['Statut actuel', transport.get_status_display()],
            ]
            ref_table = Table(ref_data, colWidths=[5*cm, 13*cm])
            ref_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#D5E8F0')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(ref_table)
            elements.append(Spacer(1, 0.5*cm))

            # ── Véhicule ──────────────────────────────────────────────────────
            elements.append(Paragraph("  VÉHICULE", section_style))
            elements.append(Spacer(1, 0.2*cm))
            v = transport.vehicle
            vehicle_data = [
                ['Titre', v.title],
                ['Marque / Modèle', f"{v.brand.name} {v.model.name}"],
                ['Année', str(v.year)],
                ['Carburant', v.get_fuel_display()],
                ['Transmission', v.get_transmission_display()],
                ['Poids estimé', f"{transport.vehicle_weight_kg} kg" if transport.vehicle_weight_kg else "Non renseigné"],
            ]
            v_table = Table(vehicle_data, colWidths=[5*cm, 13*cm])
            v_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#EEF4FF')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(v_table)
            elements.append(Spacer(1, 0.5*cm))

            # ── Client ────────────────────────────────────────────────────────
            elements.append(Paragraph("  CLIENT", section_style))
            elements.append(Spacer(1, 0.2*cm))
            client_data = [
                ['Nom', transport.client_name],
                ['Email', transport.client_email],
                ['Téléphone', transport.client_phone or '—'],
                ['Destination', transport.destination_city],
            ]
            c_table = Table(client_data, colWidths=[5*cm, 13*cm])
            c_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#EEF4FF')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(c_table)
            elements.append(Spacer(1, 0.5*cm))

            # ── Transport & Tarification ───────────────────────────────────────
            elements.append(Paragraph("  TRANSPORT & TARIFICATION", section_style))
            elements.append(Spacer(1, 0.2*cm))
            cost_data = [
                ['Pays d\'origine', f"{transport.origin_city or ''} {transport.origin_country}".strip()],
                ['Zone tarifaire', transport.zone.name if transport.zone else '—'],
                ['Délai estimé', f"{transport.zone.delay_days_min}–{transport.zone.delay_days_max} jours" if transport.zone else '—'],
                ['Coût estimé', f"{transport.estimated_cost:,.0f} FCFA" if transport.estimated_cost else '—'],
                ['Coût final', f"{transport.final_cost:,.0f} FCFA" if transport.final_cost else 'À confirmer'],
                ['Avance requise (30%)', f"{transport.advance_required:,.0f} FCFA" if transport.advance_required else '—'],
                ['Avance payée', f"{transport.advance_paid:,.0f} FCFA"],
                ['Transporteur', transport.transporter.name if transport.transporter else 'À assigner'],
            ]
            cost_table = Table(cost_data, colWidths=[5*cm, 13*cm])
            cost_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#EEF4FF')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#D5F0D5')),  # Coût final en vert
            ]))
            elements.append(cost_table)
            elements.append(Spacer(1, 0.5*cm))

            # ── Étapes de suivi ───────────────────────────────────────────────
            steps = transport.steps.all().order_by('reached_at')
            if steps:
                elements.append(Paragraph("  SUIVI DU TRANSPORT", section_style))
                elements.append(Spacer(1, 0.2*cm))
                step_data = [['Date', 'Statut', 'Détails', 'Lieu']]
                for step in steps:
                    step_data.append([
                        step.reached_at.strftime('%d/%m/%Y %H:%M'),
                        step.get_status_display(),
                        step.description or '—',
                        step.location or '—',
                    ])
                step_table = Table(step_data, colWidths=[3.5*cm, 4*cm, 7*cm, 3.5*cm])
                step_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E75B6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F9FF')]),
                    ('PADDING', (0, 0), (-1, -1), 5),
                ]))
                elements.append(step_table)
                elements.append(Spacer(1, 0.5*cm))

            # ── Mention dédouanement ──────────────────────────────────────────
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CCCCCC')))
            elements.append(Spacer(1, 0.3*cm))
            warning_style = ParagraphStyle('Warning', parent=normal,
                                           fontSize=9, textColor=colors.HexColor('#B45309'),
                                           borderColor=colors.HexColor('#F59E0B'),
                                           borderWidth=1, borderPadding=6,
                                           backColor=colors.HexColor('#FFFBEB'))
            elements.append(Paragraph(f"⚠️  {transport.customs_note}", warning_style))
            elements.append(Spacer(1, 0.3*cm))
            elements.append(Paragraph(
                f"Document généré le {timezone.now().strftime('%d/%m/%Y à %H:%M')} — Plateforme Véhicules & Pièces",
                ParagraphStyle('Footer', parent=normal, fontSize=8,
                               textColor=colors.gray, alignment=TA_CENTER)
            ))

            doc.build(elements)
            return buffer.getvalue()

        except ImportError:
            # ReportLab non installé — retourner un PDF minimal d'erreur
            return b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"