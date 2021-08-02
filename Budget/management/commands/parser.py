from rest_framework.parsers import JSONParser
from django.core.management.base import BaseCommand, CommandError
from rest_framework import serializers
from Budget.models import Budget
import requests
import io

#Переименовать проект в ApiJsonParser

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        #fields = '__all__'
        exclude = ['parentcode']

    def create(self, validated_data):
        return Budget.objects.create(**validated_data)
   #
   # def update(self, instance, validated_data):
   #     instance.code = validated_data.get('code', instance.code)
   #     instance.name = validated_data.get('name', instance.name)
   #     instance.startdate = validated_data.get('startdate', instance.startdate)
   #     instance.enddate = validated_data.get('enddate', instance.enddate)
   #     instance.status = validated_data.get('status', instance.status)
   #     instance.budgettype = validated_data.get('budgtypecode', instance.budgettype)
   #     instance.save()
   #
   #     return instance

class APIParser:
    """ Генерирует url страниц, скачивает JSON содержимое, обрабатывает и записывает в БД """
    def __init__(self):
        pass
    def urlGenerator(self):
        """
            Генерирует URL согласно полученным настройкам
        """
        return 'http://budget.gov.ru/epbs/registry/7710568760-BUDGETS/data?pageSize=100&filterstatus=ACTIVE&pageNum=1'
    def parse(self):
        """
            Запрашивает у генератора URL, отправляет запрос, получает и обрабатывает ответ, разбирает на блоки
        """
        number_page = 1
        # Цикл по генерируемым URL страниц.
        #while True:
        url = self.urlGenerator()
        session = requests.Session()
        response = session.get(url)
        if response.status_code == 200:
            stream = io.BytesIO(response.content)
            data = JSONParser().parse(stream)
            #Проходим по полученным блокам информации
            for number_block, block in enumerate(data['data']):
                #Замена значений полей на допустимые
                if not block['enddate']:
                    block['enddate'] = None
                #Замена названий соответствующих полей
                block['budgettype'] = block.pop('budgtypecode')
                in_serializer = BudgetSerializer(data=block)
                if in_serializer.is_valid():
                    #Если проходит проверку то сохраняем в бд
                    in_serializer.save()
                else:
                    #Если вызывает ошибку, то проверяем не уникален ли ключ. И если уникален, то обновляем элемент с этим ключом
                    if list(in_serializer.errors.keys())[0] == 'code':
                        for budget in Budget.objects.all().filter(code=block['code']):
                            if budget.code == block['code']:
                                in_serializer = BudgetSerializer(budget, data=block)
                                in_serializer.is_valid()
                                in_serializer.save()



        elif response.status_code == 404:
            
            print('Страница с номером {number_page} недоступна.')
        



class Command(BaseCommand):
    help = 'Парсинг'

    def handle(self, *args, **options):
        parser = APIParser()
        parser.parse()