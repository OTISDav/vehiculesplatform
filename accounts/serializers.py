from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, KYCDocument


class RegisterSerializer(serializers.ModelSerializer):
    #----Inscription d'un nouveau client
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label="Confirmation mot de passe")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'city', 'country', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.username = validated_data['email']  # username = email
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    #----Profil du client connecte
    kyc_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'email',
            'phone', 'city', 'country',
            'is_kyc_verified', 'kyc_status',
            'date_joined'
        )
        read_only_fields = ('email', 'is_kyc_verified', 'date_joined')

    def get_kyc_status(self, obj):
        if hasattr(obj, 'kyc'):
            return obj.kyc.status
        return None


class KYCSubmitSerializer(serializers.ModelSerializer):
    #----Soumission du dossier KYC par le client

    class Meta:
        model = KYCDocument
        fields = ('id_card_front', 'id_card_back', 'driving_license', 'selfie')

    def create(self, validated_data):
        user = self.context['request'].user
        #----Supprimer l'ancien dossier s'il existe
        KYCDocument.objects.filter(user=user).delete()
        return KYCDocument.objects.create(user=user, **validated_data)


class KYCStatusSerializer(serializers.ModelSerializer):
    #----Statut KYC visible par le client

    class Meta:
        model = KYCDocument
        fields = ('status', 'admin_note', 'submitted_at', 'reviewed_at')
        read_only_fields = fields