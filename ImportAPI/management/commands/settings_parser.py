from ImportAPI.models import Budget, GlavBudgetClass

"""
    Настройки парсера
"""

class SettingsImportBudget:
    """ Настройки парсера budget"""
    base_url = 'http://budget.gov.ru/epbs/registry/7710568760-BUDGETS/data'
    # Дополнительные условия поиска писать по порядку, разделяя символом '&'
    conditions_url = 'filterstatus=ACTIVE'
    # Указывать изменяемые поля занесением словарей с ключами 'json_field' и 'model_field' в список
    replacing_fields = [
                        {'json_field': 'budgtypecode',
                         'model_field': 'budgettype'},
                       ]
    # Указывать изменяемые значения полей занесением словарей с ключами 'json_field', 'old_value', 'new_value' в список
    replacing_field_values = [
                        {'json_field': 'enddate',
                         'old_value': '',
                         'new_value': None},
                             ]
    # Поле с уникальным значением по которому парсер определяет, что поле уже загружено
    unique_field = 'code'
    # Поле с датой, по которой определяется перезаписывать ли запись в БД или оставить старую
    date_field = 'loaddate'
    # Формат даты
    date_format = '%Y-%m-%d %H:%M:%S.%f'

    """ Настройки сериалайзера """
    # Используемая модель БД
    use_model = Budget
    # Выбирается либо список полей, либо список исключёных полей. Второе значение определятся как ''
    fields = '__all__'
    exclude = []
    # Поиск родительского значения
    search_parent = True
    # поле по которому производится поиск
    search_parentcode = 'code'
    json_parent_field = 'parentcode'


class SettingsImportGlavBudget:
    """ Настройки парсера GlavBudget"""
    base_url = 'http://budget.gov.ru/epbs/registry/7710568760-BUDGETCLASGRBSFB/data'
    # Дополнительные условия поиска писать по порядку, разделяя символом '&'
    conditions_url = ''
    # Указывать изменяемые поля занесением словарей с ключами 'json_field' и 'model_field' в список
    replacing_fields = [
                        {'json_field': 'budgetname',
                         'model_field': 'budget'},
                       ]
    # Указывать изменяемые значения полей занесением словарей с ключами 'json_field', 'old_value', 'new_value' в список
    replacing_field_values = [
                        {'json_field': 'enddate',
                         'old_value': '',
                         'new_value': None},
                             ]
    # Поле с уникальным значением по которому парсер определяет, что поле уже загружено
    unique_field = 'code'
    # Поле с датой, по которой определяется перезаписывать ли запись в БД или оставить старую
    date_field = "startdate"
    # Формат даты
    date_format = '%Y-%m-%d %H:%M:%S.%f'

    """ Настройки сериалайзера """
    # Используемая модель БД
    use_model = GlavBudgetClass
    # Выбирается либо список полей, либо список исключёных полей. Второе значение определятся как ''
    fields = '__all__'
    exclude = []
    # Поиск родительского значения
    search_parent = False
    # поле по которому производится поиск
    search_parentcode = ''
    json_parent_field = ''



class SettingsImportAPI(SettingsImportBudget):
    """ Настройки парсера API. Наследуется от нужных настроек"""

