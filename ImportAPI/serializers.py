from rest_framework import serializers
from ImportAPI.management.commands.settings_parser import SettingsImportAPI

class UploadedAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingsImportAPI.use_model
        fields = '__all__'

