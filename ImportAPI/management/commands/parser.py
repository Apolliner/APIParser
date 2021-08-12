from rest_framework.parsers import JSONParser
from django.core.management.base import BaseCommand
from rest_framework import serializers
from datetime import datetime
import requests
import io
import time
from ImportAPI.management.commands.settings_parser import SettingsImportAPI
from rest_framework.fields import empty

class AssemblerSerializer():
    """
        Собирает сериализатор с нужными параметрами поиска и замены полей
    """
    def __init__(self, model, fields_mapping):
        self.model = model
        self.fields_mapping = fields_mapping

    class BaseAPISerializer(serializers.ModelSerializer):
        """ Базовый сериализатор"""
        def __init__(self, instance=None, data=empty, **kwargs):
            """
                При нобходимости заменяет значения полей в полученных данных, определяет родительский элемент и
                наличие такого же элемента в БД, самостоятельно определяя создание нового элемента или обновление старого.
            """
            data = self.fixed_field(data)
            data = self.fixed_date_field(data)
            data = self.search_parent(data)
            instance, data = self.search_in_model(instance, data)
            super().__init__(instance, data, **kwargs)

        def fixed_field(self, data):
            """ Пустышка """
            return data

        def fixed_date_field(self, data):
            """ Пустышка """
            return data

        def search_parent(self, data):
            """ Пустышка """
            return data

        def search_in_model(self, instance, data):
            """ Пустышка """
            return instance, data

    class APISerializer(BaseAPISerializer):
        """ Сериализатор для переопределния методов и полей"""
        class Meta:
            pass

    def get_serializer(self):
        """ Возвращает сериализатор с нужными настройками"""
        serializer = self.APISerializer
        serializer.Meta.model = self.model
        serializer.Meta.fields = self.get_fields()
        serializer.Meta.extra_kwargs = self.get_extra_kwargs()
        # Определение того надо ли заменять значения полей
        all_fixed_fields = self.get_fixed_fiels()
        if all_fixed_fields:
            serializer._all_fixed_fields = all_fixed_fields
            setattr(serializer, 'fixed_field', fixed_field)
        # Определение того надо ли именять формат дат
        date_fields, date_format = self.get_fixed_date()
        if date_fields:
            serializer._date_fields = date_fields
            serializer._date_format = date_format
            setattr(serializer, 'fixed_date_field', fixed_date_field)
        # Определение того надо ли искать родительский элемент
        parent_field = self.get_search_parent()
        if parent_field:
            serializer._parent_field = parent_field
            setattr(serializer, 'search_parent', search_parent)
        # Определение остальных важных настроек
        unique_field, comparison_field = self.get_outher_settings()
        if unique_field:
            serializer._unique_field = unique_field
            serializer._comparison_field = comparison_field
            setattr(serializer, 'search_in_model', search_in_model)
        return serializer
    def get_fields(self):
        """ Возвращает список используемых полей"""
        fields = []
        for field in self.fields_mapping:
            fields.append(field['json_field'])
        return fields

    def get_extra_kwargs(self):
        """ Возвращает список extra_kwargs """
        extra_kwargs = dict()
        for field in self.fields_mapping:
            if field['json_field'] != field['to_field']:
                extra_kwargs[field['json_field']] = {'source': field['to_field']}
        return extra_kwargs

    def get_fixed_fiels(self):
        """ Определяет наличие заменяемых полей и возвращает словарь {'field': {'old_value': 'new_value'}}"""
        all_fixed_fields = dict()
        for field in self.fields_mapping:
            if field['values_map']:
                all_fixed_fields[field['json_field']] = field['values_map']
        return all_fixed_fields

    def get_fixed_date(self):
        """ Определяет наличие заменяемых дат, на указанный формат"""
        date_fields = []
        date_format = ''
        for field in self.fields_mapping:
            if field['fixed_date']:
                date_fields.append(field['json_field'])
                date_format = field['fixed_date']
        return date_fields, date_format

    def get_search_parent(self):
        """ Определяет требуется ли поиск родительского элемента"""
        for field in self.fields_mapping:
            if field['parent']:
                return field['json_field']

    def get_outher_settings(self):
        """ Возвращает остальные важные настройки"""
        unique_field = ''
        comparison_field = ''
        for field in self.fields_mapping:
            if field['unique']:
                unique_field = field['json_field']
            elif field['comparison']:
                comparison_field = field['json_field']
        return unique_field, comparison_field

def fixed_field(self, data):
    """ Изменяет значения полей на допустимые """
    if data is not empty:
        for field in self._all_fixed_fields:
            if data[field] in self._all_fixed_fields[field].keys():
                data[field] = self._all_fixed_fields[field][data[field]]
    return data

def fixed_date_field(self, data):
    """ Изменяет формат полей datetime на допустимые """
    if data is not empty:
        for date_field in self._date_fields:
            if data[date_field] != None:
                data[date_field] = datetime.strptime(data[date_field], self._date_format)
    return data

def search_parent(self, data):
    """ Ищет родительский элемент"""
    if data is not empty:
        if data[self._parent_field]:
            parent = self.Meta.model.objects.filter(
                code__icontains=int(data[self._parent_field]))
            if parent:
                data[self._parent_field] = parent[0].id
            else:
                data[self._parent_field] = ''
    return data

def search_in_model(self, instance, data):
    """ Ищет в модели уже существующий элемент и при нахождении возвращает его. Иначе возвращает None"""
    if instance is None and data != empty:
        in_model = self.Meta.model.objects.filter(code=data[self._unique_field])
        if in_model:
            # Проверка на "свежесть" имеющейся записи
            if data[self._comparison_field] > getattr(in_model[0], self._comparison_field):
                return in_model[0], data
            # Проверка на найденный при повторном проходе родительский элемент
            if data[self._parent_field] != '' and data[self._parent_field] != getattr(in_model[0], self._parent_field):
                return in_model[0], data
            else: #Если получаемая запись не актуальна
                return None, None
        else: #Если записи нет в бд
            return None, data
    return instance, data


class APIParser:
    """ Генерирует url страниц, скачивает JSON содержимое, обрабатывает и записывает в БД """
    len_page = 1000
    serializer = AssemblerSerializer(SettingsImportAPI.use_model, SettingsImportAPI.mapping_fields).get_serializer()

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