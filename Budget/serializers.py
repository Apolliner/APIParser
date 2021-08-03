from rest_framework import serializers
from Budget.management.commands.settings_parser import SettingsImportAPI

class UploadedAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingsImportAPI.use_model
        fields = SettingsImportAPI.fields

