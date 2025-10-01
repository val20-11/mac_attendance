from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import UserProfile
import re

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['account_number', 'user_type', 'full_name', 'career', 'semester']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']

class LoginSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=7, min_length=7)
    password = serializers.CharField()
    
    def validate_account_number(self, value):
        if not re.match(r'^\d{7}$', value):
            raise serializers.ValidationError('El número de cuenta debe tener exactamente 7 dígitos.')
        return value
    
    def validate(self, data):
        account_number = data.get('account_number')
        password = data.get('password')
        
        if account_number and password:
            # Buscar el perfil por número de cuenta
            try:
                profile = UserProfile.objects.get(account_number=account_number)
                user = authenticate(username=profile.user.username, password=password)
                if not user:
                    raise serializers.ValidationError('Número de cuenta o contraseña incorrectos.')
                if not user.is_active:
                    raise serializers.ValidationError('Esta cuenta está desactivada.')
                data['user'] = user
            except UserProfile.DoesNotExist:
                raise serializers.ValidationError('Número de cuenta no encontrado.')
        else:
            raise serializers.ValidationError('Debe incluir número de cuenta y contraseña.')
        
        return data