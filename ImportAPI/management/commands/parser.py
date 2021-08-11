from rest_framework.parsers import JSONParser
from django.core.management.base import BaseCommand
from rest_framework import serializers
from datetime import datetime
import requests
import io
import time
import inspect
from ImportAPI.management.commands.settings_parser import SettingsImportAPI




class APISerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='code')
    budgettype = serializers.SerializerMethodField(source='budgtypecode')
    #def get_name(self, instance):
    #    print(F"instance - {instance}")
    #    return 'jgbnsdljfndsnvdzkfvn '
    class Meta:
        model = SettingsImportAPI.use_model
        if SettingsImportAPI.fields:
            fields = SettingsImportAPI.fields
        else:
            exclude = SettingsImportAPI.exclude

    def create(self, validated_data):
        return SettingsImportAPI.use_model.objects.create(**validated_data)



class TestSerializer(serializers.ModelSerializer):
    all_fixed_fields = {'enddate': {'': None}}
    class Meta:
        model = SettingsImportAPI.use_model
        fields = ("code", "name", "budgtypecode", "enddate", "startdate", "status", "loaddate", "parentcode")
        extra_kwargs = {
            "budgtypecode": {"source": "budgettype"},
        }
    def fixed_field(self):
        #Изменяет значения полей на допустимые
        if self.initial_data['enddate'] == '':
            self.initial_data['enddate'] = None
        #for field in self.initial_data:
        #    if field in self.all_fixed_fields:
        #        if field == self.all_fixed_fields[field]:
        #            self.initial_data[field] = self.all_fixed_fields[field][self.all_fixed_fields[field]]

        #for field in self.all_fixed_fields:
        #    if self.initial_data[field] == self.all_fixed_fields[field]:
        #        print(F"self.initial_data[field] - {self.initial_data[field]}, self.all_fixed_fields[field] - {self.all_fixed_fields[field]}")
        #        self.initial_data[field] = self.all_fixed_fields[field][self.initial_data[field]]
        #        print(
        #            F"self.initial_data[field] - {self.initial_data[field]} \n")






class APIParser:
    """ Генерирует url страниц, скачивает JSON содержимое, обрабатывает и записывает в БД """
    len_page = 10
    serializer = TestSerializer

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
        #print(self.serializer.get_fields(self.serializer))
        #print(repr(self.serializer()))
        #print(f"\n\nМетоды - {inspect.getmembers(self.serializer, predicate=inspect.ismethod)}\n\n")
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
                    #self.replacingFieldsValues(block)
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
                            in_serializer.fixed_field()
                            if in_serializer.is_valid(raise_exception=True):
                                in_serializer.save()
                            else:
                                print(F"Ошибка валидации обновляемой записи - {in_serializer.errors.keys()}")
                    else:
                        in_serializer = self.serializer(data=block)
                        in_serializer.fixed_field()
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