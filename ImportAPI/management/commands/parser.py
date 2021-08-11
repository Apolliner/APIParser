from rest_framework.parsers import JSONParser
from django.core.management.base import BaseCommand
from rest_framework import serializers
from datetime import datetime
import requests
import io
import time
from ImportAPI.management.commands.settings_parser import SettingsImportAPI
from rest_framework.fields import empty


class TestSerializer(serializers.ModelSerializer):
    all_fixed_fields = {'enddate': {'': None}}

    def __init__(self, instance=None, data=empty, **kwargs):
        """
            Заменяет значения полей в полученных данных, определяет родительский элемент и
            наличие такого же элемента в БД, самостоятельно определяя создание нового элемента или обновление старого.
        """
        if data is not empty:
            data = self.fixed_field(data)
            data = self.search_parent(data)
        if instance is None:
            instance, data = self.search_in_model(data)
        super().__init__(instance, data, **kwargs)


    class Meta:
        model = SettingsImportAPI.use_model
        fields = ("code", "name", "budgtypecode", "enddate", "startdate", "status", "loaddate", "parentcode")
        extra_kwargs = {
            "budgtypecode": {"source": "budgettype"},
        }

    def search_in_model(self, data):
        """ Ищет в модели уже существующий элемент и при нахождении возвращает его. Иначе возвращает None"""
        in_model = self.Meta.model.objects.filter(code=data[SettingsImportAPI.unique_field])
        if in_model:
            if data['loaddate'] > getattr(in_model[0], SettingsImportAPI.date_field):
                return in_model[0], data
            else:
                return None, None
        else:
            return None, data

    def fixed_field(self, data):
        """ Изменяет значения полей на допустимые """
        if data['enddate'] == '':
            data['enddate'] = None
        data[SettingsImportAPI.date_field] = datetime.strptime(data[SettingsImportAPI.date_field],
                                                               SettingsImportAPI.date_format)
        return data

    def search_parent(self, data):
        """ Ищет родительский элемент"""
        if data[SettingsImportAPI.json_parent_field]:
            parent = SettingsImportAPI.use_model.objects.filter(
                code__icontains=int(data[SettingsImportAPI.json_parent_field]))
            if parent:
                data[SettingsImportAPI.json_parent_field] = parent[0].id
            else:
                data[SettingsImportAPI.json_parent_field] = ''
        return data


class APIParser:
    """ Генерирует url страниц, скачивает JSON содержимое, обрабатывает и записывает в БД """
    len_page = 1000
    serializer = TestSerializer

    def url_generator(self, number_page):
        """ Генерирует URL согласно полученным настройкам """
        return f'{SettingsImportAPI.base_url}?pageSize={self.len_page}&pageNum={number_page}&{SettingsImportAPI.conditions_url}'

    def parse(self):
        """ Запрашивает у генератора URL, отправляет запрос, получает и обрабатывает ответ, разбирает на блоки """
        start = time.time()
        number_page = 1
        # Цикл по генерируемым URL страниц.
        while True:
            url = self.url_generator(number_page)
            session = requests.Session()
            response = session.get(url)
            data = {'data': ''}
            if response.status_code == 200:
                stream = io.BytesIO(response.content)
                data = JSONParser().parse(stream)
                #Проходим по полученным блокам информации
                for number_block, block in enumerate(data['data']):
                    in_serializer = self.serializer(data=block)
                    if in_serializer.initial_data != None:
                        if in_serializer.is_valid(raise_exception=True):
                            # Если проходит проверку то сохраняем в бд
                            in_serializer.save()
                        else:
                            print(F"Ошибка валидации новой записи- {in_serializer.errors.keys()}")
            elif response.status_code == 404:
                print('Страница с номером {number_page} недоступна.')
            #Если на странице меньше записей чем указанный размер страницы
            if len(data['data']) != self.len_page:
                break
            print(F"Обработана страница - {number_page}")
            number_page += 1
        finish = time.time()
        print(F"Загрузка завершена. Время загрузки: {round(finish - start, 1)} секунд")


class Command(BaseCommand):
    help = 'Парсинг'

    def handle(self, *args, **options):
        parser = APIParser()
        parser.parse()