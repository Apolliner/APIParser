"""
    Настройки парсера
"""
class FieldsMappingSerializer(serializers.ModelSerializer):
    class Meta:
    fields_map = {
    #'поле_модели': {'json_field': 'поле_json', 'to_model': 'в какой модели ищем', 'to_field': 'поле для поиска', 'values_map': {'какое значение': 'на какое заменяем'}},
    'code': {'json_field': 'code', 'to_model': 'Budget', 'to_field': 'code', 'values_map': {'какое значение': 'на какое заменяем'}},
    'name': {'json_field': 'name', 'to_model': 'Budget', 'to_field': 'code', 'values_map': {'какое значение': 'на какое заменяем'}},
    'startdate': {'json_field': 'startdate', 'to_model': 'Budget', 'to_field': 'startdate', 'values_map': {'какое значение': 'на какое заменяем'}},
    'enddate': {'json_field': 'enddate', 'to_model': 'Budget', 'to_field': 'enddate', 'values_map': {'какое значение': 'на какое заменяем'}},
    'status': {'json_field': 'status', 'to_model': 'Budget', 'to_field': 'status', 'values_map': {'какое значение': 'на какое заменяем'}},
    'budgettype': {'json_field': 'budgtypecode', 'to_model': 'Budget', 'to_field': 'budgettype', 'values_map': {'какое значение': 'на какое заменяем'}},
    }



class APIImport:
    """(возможно имя не лучшее) который отвечает за взаимодействие через api, а также по заданным настройкам создает экземпляр FieldsMappingSerializer
    Пример использования класса
    """
    url = 'http://budget.gov.ru/epbs/registry/7710568760-BUDGETS/data?pageSize=10&filterstatus=ACTIVE&pageNum=1'
    model = models.Budget
    fields_mapping = {
    'parentcode': {'json_field': 'parentcode', 'to_field': 'code', 'values_map': {'00000000': None}},
    'budgettype': {'json_field': 'budgtypecode', 'values_map': {'11': BudgetType.CITY, '12': BudgetType.LOCAL, '13': BudgetType.LOCAL, '14': BudgetType.LOCAL}},
    'id': {'json_field': 'code', 'to_field': 'code'}}
import_ = api_import.APIImport(url, model, fields_mapping).make_import()