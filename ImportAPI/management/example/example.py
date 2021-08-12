from collections import OrderedDict


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
    myserializer = serializer_factory(
        use_model, fields='__all__',
        owner=HiddenField(default=CurrentUserDefault()),
    )
    return myserializer







class FieldsMappingSerializer(serializers.ModelSerializer):
    class Meta:
    fields_map = {
    'поле_модели': {'json_field': 'поле_json', 'to_model': 'в какой модели ищем', 'to_field': 'поле для поиска', 'values_map': {'какое значение': 'на какое заменяем'}},
    }



class APIImport:
    url = 'http://budget.gov.ru/epbs/registry/7710568760-BUDGETS/data?pageSize=1000&filterstatus=ACTIVE&pageNum=1'
    model = models.Budget
    fields_mapping = {
    'parentcode': {'json_field': 'parentcode', 'to_field': 'code', 'values_map': {'00000000': None}},
    'budgettype': {'json_field': 'budgtypecode', 'values_map': {'11': BudgetType.CITY, '12': BudgetType.LOCAL, '13': BudgetType.LOCAL, '14': BudgetType.LOCAL}},
    'id': {'json_field': 'code', 'to_field': 'code'}}
    import_ = api_import.APIImport(url, model, fields_mapping).make_import()





from rest_framework.parsers import JSONParser
from django.core.management.base import BaseCommand
from rest_framework import serializers
from datetime import datetime
import requests
import io
import time
import inspect
from ImportAPI.management.commands.settings_parser import SettingsImportAPI


def assembler_serializer():
    """
        Собирает сериализатор с нужными параметрами поиска и замены полей
    """

    class MySerializer(serializers.ModelSerializer):
        """ Базовый сериализатор"""
        class Meta:
            model = SettingsImportAPI.use_model
            fields = SettingsImportAPI.fields
    def fabric_get_parent_method(field, parent_field, use_model, serializer):
        """
            Принимает имя метода и используемую модель, возвращает метод get_<field_name>,
            работающий с выбранной моделью и полем
        """
        def get_base_parent(self, instance):
            """
                Базовый метод для создания обработки поля
            """
            parent = use_model.objects.filter(
                code__icontains=int(instance[parent_field]))
            print(F"use_model - {use_model}, parent - {parent}")
            if parent:
                print(f"parent[0].id - {parent[0].id}")
                return parent[0].id
            else:
                return None

        setattr(serializer, f"get_{field}", get_base_parent.__get__(serializer, type(serializer)))
        return serializer

    serializer = MySerializer
    for mapping_field in SettingsImportAPI.mapping_fields:
        if mapping_field['parent']: # Если есть заменяемые значения поля
            # Добавление собираемого на фабрике метода get_<field_name>
            #MySerializer = fabric_get_parent_method(mapping_field['to_field'], mapping_field['parent'],
            #                                      SettingsImportAPI.use_model, serializer)
            # Добавление поля, обращающегося к методу get_<field_name>
            setattr(serializer, mapping_field['to_field'], serializers.SerializerMethodField(source='20'))
        #elif mapping_field['values_map']: # Если есть заменяемые значения полей
        #    pass
        else: # Замена имени поля
            setattr(serializer, mapping_field['json_field'],
                    serializers.SerializerMethodField(source=mapping_field['to_field']))
    return serializer



class APISerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(method_name='get_name')
    def get_name(self, instance):
        print(F"instance - {instance}")
        return 'jgbnsdljfndsnvdzkfvn '
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
    len_page = 10
    serializer = APISerializer

    def replacingFieldsValues(self, block):
        """ Заменяет список указанных в параметрах значений полей"""
        if SettingsImportAPI.replacing_field_values:
            for replace in SettingsImportAPI.replacing_field_values:
                if block[replace['json_field']] == replace['old_value']:
                    block[replace['json_field']] = replace['new_value']

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
        #print(self.serializer.get_parentcode({'code': '1'}))
        #print(self.serializer.parentcode)
        #print(self.serializer.enddate)
        print(f"\n\nМетоды - {inspect.getmembers(self.serializer, predicate=inspect.ismethod)}\n\n")
        # Цикл по генерируемым URL страниц.
        while True:
            url = self.urlGenerator(number_page)
            session = requests.Session()
            response = session.get(url)
            data = {'data': ''}
            if response.status_code == 200:
                stream = io.BytesIO(response.content)
                data = JSONParser().parse(stream)
                #Проходим по полученным блокам информации
                for number_block, block in enumerate(data['data']):
                    #Замена значений полей на допустимые
                    self.replacingFieldsValues(block)
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
                            in_serializer = self.serializer(model_obj, data=block)
                            if in_serializer.is_valid(raise_exception=True):
                                in_serializer.save()
                            else:
                                print(F"Ошибка валидации обновляемой записи - {in_serializer.errors.keys()}")
                    else:
                        in_serializer = self.serializer(data=block)
                        if in_serializer.is_valid(raise_exception=True):
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



class FabricSerializer():
    """
        Собирает сериализатор с нужными параметрами поиска и замены полей
    """
    _all_fixed_fields = ''
    _parent_field = ''
    _date_fields = ''
    _date_format = ''
    _unique_field = ''
    _replacing_field_values = ''
    _comparison_field = ''
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
            serializer.fixed_field = self.fixed_field
        # Определение того надо ли именять формат дат
        date_fields, date_format = self.get_fixed_date()
        if date_fields:
            serializer._date_fields = date_fields
            serializer._date_format = date_format
            serializer.fixed_date_field = self.fixed_date_field
        # Определение того надо ли искать родительский элемент
        parent_field = self.get_search_parent()
        if parent_field:
            serializer._parent_field = parent_field
            serializer.search_parent = self.search_parent
        # Определение остальных важных настроек
        unique_field, comparison_field = self.get_outher_settings()
        if unique_field:
            serializer._unique_field = unique_field
            serializer._comparison_field = comparison_field
            serializer.search_in_model = self.search_in_model
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

    def fixed_field(self, data):
        """ Изменяет значения полей на допустимые """
        if data is not empty:
            for field in self._all_fixed_fields:
                if data[field] in self._all_fixed_fields[field].keys():
                    data[field] = self._all_fixed_fields[field][data[field]]
        return data

    def get_fixed_date(self):
        """ Определяет наличие заменяемых дат, на указанный формат"""
        date_fields = []
        date_format = ''
        for field in self.fields_mapping:
            if field['fixed_date']:
                date_fields.append(field['json_field'])
                date_format = field['fixed_date']
        return date_fields, date_format

    def fixed_date_field(self, data):
        """ Изменяет формат полей datetime на допустимые """
        if data is not empty:
            for date_field in self._date_fields:
                data[date_field] = datetime.strptime(data[date_field], self._date_format)
        return data

    def get_search_parent(self):
        """ Определяет требуется ли поиск родительского элемента"""
        for field in self.fields_mapping:
            if field['parent']:
                return field['json_field']

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

    def search_in_model(self, instance, data):
        """ Ищет в модели уже существующий элемент и при нахождении возвращает его. Иначе возвращает None"""
        if instance is None:
            in_model = self.model.objects.filter(code=data[self._unique_field])
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

    class TestSerializer(serializers.ModelSerializer):
        _all_fixed_fields = {'enddate': {'': None}}
        _parent_field = SettingsImportAPI.json_parent_field
        _date_fields = SettingsImportAPI.date_field
        _date_format = SettingsImportAPI.date_format
        _unique_field = SettingsImportAPI.unique_field
        _replacing_field_values = SettingsImportAPI.replacing_field_values
        _comparison_field = 'loaddate'

        def __init__(self, instance=None, data=empty, **kwargs):
            """
                Заменяет значения полей в полученных данных, определяет родительский элемент и
                наличие такого же элемента в БД, самостоятельно определяя создание нового элемента или обновление старого.
            """
            data = self.fixed_field(data)
            data = self.fixed_date_field(data)
            data = self.search_parent(data)
            instance, data = self.search_in_model(instance, data)
            super().__init__(instance, data, **kwargs)

        class Meta:
            model = SettingsImportAPI.use_model
            fields = ("code", "name", "budgtypecode", "enddate", "startdate", "status", "loaddate", "parentcode")
            extra_kwargs = {
                "budgtypecode": {"source": "budgettype"},
            }

        def search_in_model(self, instance, data):
            """ Ищет в модели уже существующий элемент и при нахождении возвращает его. Иначе возвращает None"""
            if instance is None:
                in_model = self.Meta.model.objects.filter(code=data[self._unique_field])
                if in_model:
                    # Проверка на "свежесть" имеющейся записи
                    if data[self._comparison_field] > getattr(in_model[0], self._comparison_field):
                        return in_model[0], data
                    # Проверка на найденный при повторном проходе родительский элемент
                    if data[self._parent_field] != '' and data[self._parent_field] != getattr(in_model[0],
                                                                                              self._parent_field):
                        return in_model[0], data
                    else:  # Если получаемая запись не актуальна
                        return None, None
                else:  # Если записи нет в бд
                    return None, data
            return instance, data

        def fixed_field(self, data):
            """ Изменяет значения полей на допустимые """
            if data is not empty:
                for field in self._replacing_field_values:
                    if data[field] in self._replacing_field_values[field].keys():
                        data[field] = self._replacing_field_values[field][data[field]]
            return data

        def fixed_date_field(self, data):
            """ Изменяет формат полей datetime на допустимые """
            if data is not empty:
                for date_field in self._date_fields:
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