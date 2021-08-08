from rest_framework.parsers import JSONParser
from django.core.management.base import BaseCommand, CommandError
from django import db
from rest_framework import serializers
from datetime import datetime
import pytz
import requests
import io
import time
import collections
from ImportAPI.management.commands.settings_parser import SettingsImportAPI

def serializer_factory(use_model, fields=None, **kwargs):
    def _get_declared_fields(attrs):
        if fields == '__all__':
            pass
        else:
            fields = [(field_name, attrs.pop(field_name))
                      for field_name, obj in list(attrs.items())
                      if isinstance(obj, Field)]
            fields.sort(key=lambda x: x[1]._creation_counter)
        return OrderedDict(fields)
    class Base(object):
        pass
    Base._declared_fields = _get_declared_fields(kwargs)
    class MySerializer(Base, ModelSerializer):
        class Meta:
            model = use_model
        if fields:
            setattr(Meta, "fields", fields)
    return MySerializer

def typebase_serializer_factory(use_model):
    serializer_factory(
        use_model, fields='__all__',
        owner=HiddenField(default=CurrentUserDefault()),
    )
    return myserializer


class APISerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingsImportAPI.use_model
        if SettingsImportAPI.fields:
            fields = SettingsImportAPI.fields
        else:
            exclude = SettingsImportAPI.exclude

    def create(self, validated_data):
        return SettingsImportAPI.use_model.objects.create(**validated_data)


class APIParser:
    """ Генерирует url страниц, скачивает JSON содержимое, обрабатывает и записывает в БД """
    len_page = 1000
    def replacingFieldsValues(self, block):
        """ Заменяет список указанных в параметрах значений полей"""
        if SettingsImportAPI.replacing_field_values:
            for replace in SettingsImportAPI.replacing_field_values:
                if block[replace['json_field']] == replace['old_value']:
                    block[replace['json_field']] = replace['new_value']
    def replacingFields(self, block):
        """ Заменяет список указанных в параметрах полей"""
        if SettingsImportAPI.replacing_fields:
            for replace in SettingsImportAPI.replacing_fields:
                block[replace['model_field']] = block.pop(replace['json_field'])
    def searchParent(self, block):
        parent = SettingsImportAPI.use_model.objects.filter(
            code__icontains=int(block[SettingsImportAPI.json_parent_field]))
        if parent:
            block[SettingsImportAPI.json_parent_field] = parent[0].id
        else:
            block[SettingsImportAPI.json_parent_field] = ''
    def urlGenerator(self, number_page):
        """ Генерирует URL согласно полученным настройкам """
        return f'{SettingsImportAPI.base_url}?pageSize={self.len_page}&pageNum={number_page}&{SettingsImportAPI.conditions_url}'
    def parse(self):
        """ Запрашивает у генератора URL, отправляет запрос, получает и обрабатывает ответ, разбирает на блоки """
        start = time.time()
        number_page = 1
        # Цикл по генерируемым URL страниц.
        while True:
            url = self.urlGenerator(number_page)
            session = requests.Session()
            response = session.get(url)
            if response.status_code == 200:
                stream = io.BytesIO(response.content)
                data = JSONParser().parse(stream)
                #Проходим по полученным блокам информации
                for number_block, block in enumerate(data['data']):
                    #Замена значений полей на допустимые
                    self.replacingFieldsValues(block)
                    #Замена названий соответствующих полей
                    self.replacingFields(block)
                    # Поиск родительского элемента
                    if SettingsImportAPI.search_parent and block[SettingsImportAPI.json_parent_field]:
                        self.searchParent(block)
                    #Проверяем нет ли такого же элемента
                    not_unique = SettingsImportAPI.use_model.objects.filter(code=block[SettingsImportAPI.unique_field])
                    if not_unique:
                        model_obj = not_unique[0]
                        # Перевод даты в нужный для сравнения формат
                        date = datetime.strptime(block[SettingsImportAPI.date_field], SettingsImportAPI.date_format)
                        # Если совпадают коды и дата загрузки больше, чем записанная в БД
                        if getattr(model_obj, SettingsImportAPI.unique_field) == block[
                            SettingsImportAPI.unique_field] and date > getattr(model_obj, SettingsImportAPI.date_field):
                            in_serializer = APISerializer(model_obj, data=block)
                            if in_serializer.is_valid():
                                in_serializer.save()
                            else:
                                print(F"Ошибка валидации обновляемой записи - {in_serializer.errors.keys()}")
                    else:
                        in_serializer = APISerializer(data=block)
                        if in_serializer.is_valid():
                            #Если проходит проверку то сохраняем в бд
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