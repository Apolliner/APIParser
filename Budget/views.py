from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import viewsets, renderers
from Budget.serializers import UploadedAPISerializer
from Budget.management.commands.settings_parser import SettingsImportAPI

class UploadedAPIViewSet(viewsets.ModelViewSet):
    """
        Автоматическое предоставление действий "запрос", "создание", " извлечение`,
        `обновление` и `уничтожение`.
    """
    queryset = SettingsImportAPI.use_model.objects.all()
    serializer_class = UploadedAPISerializer

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        uploaded_api = self.get_object()
        return Response(uploaded_api.highlighted)
