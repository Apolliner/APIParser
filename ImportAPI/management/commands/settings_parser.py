from ImportAPI.models import Budget, GlavBudgetClass

"""
    Настройки парсера
"""


class SettingsImportBudget:
    """ Настройки парсера budget"""
    base_url = 'http://budget.gov.ru/epbs/registry/7710568760-BUDGETS/data'
    # Дополнительные условия поиска писать по порядку, разделяя символом '&'
    conditions_url = 'filterstatus=ACTIVE'

    """ Настройки сериализатора """
    # Используемая модель БД
    use_model = Budget
    #Обновлённая замена полей
    mapping_fields = [

        {'json_field': 'code', 'to_field': 'code', 'values_map': '', 'parent': '',
         'fixed_date': '', 'comparison': False, 'unique': True},

        {'json_field': 'name', 'to_field': 'name', 'values_map': '', 'parent': '',
         'fixed_date': '', 'comparison': False, 'unique': False},

        {'json_field': 'startdate', 'to_field': 'startdate', 'values_map': '', 'parent': '',
         'fixed_date': '%Y-%m-%d %H:%M:%S.%f', 'comparison': False, 'unique': False},

        {'json_field': 'enddate', 'to_field': 'enddate', 'values_map': {'': None}, 'parent': '',
         'fixed_date': '%Y-%m-%d %H:%M:%S.%f', 'comparison': False, 'unique': False},

        {'json_field': 'status', 'to_field': 'status', 'values_map': '', 'parent': '',
         'fixed_date': '', 'comparison': False, 'unique': False},

        {'json_field': 'budgtypecode', 'to_field': 'budgettype', 'values_map': '', 'parent': '',
         'fixed_date': '', 'comparison': False, 'unique': False},

        {'json_field': 'loaddate', 'to_field': 'loaddate', 'values_map': '', 'parent': '',
         'fixed_date': '%Y-%m-%d %H:%M:%S.%f', 'comparison': True, 'unique': False},

        {'json_field': 'parentcode', 'to_field': 'parentcode', 'values_map': '', 'parent': 'code',
         'fixed_date': '', 'comparison': False, 'unique': False},

        ]


class SettingsImportGlavBudget:
    """ Настройки парсера GlavBudget"""
    base_url = 'http://budget.gov.ru/epbs/registry/7710568760-BUDGETCLASGRBSFB/data'
    # Дополнительные условия поиска писать по порядку, разделяя символом '&'
    conditions_url = ''
    """ Настройки сериализатора """
    # Используемая модель БД
    use_model = GlavBudgetClass
    # Обновлённая замена полей
    mapping_fields = [

        {'json_field': 'code', 'to_field': 'code', 'values_map': '', 'parent': '',
         'fixed_date': '', 'comparison': False, 'unique': True},

        {'json_field': 'name', 'to_field': 'name', 'values_map': '', 'parent': '',
         'fixed_date': '', 'comparison': False, 'unique': False},

        {'json_field': 'startdate', 'to_field': 'startdate', 'values_map': '', 'parent': '',
         'fixed_date': '%Y-%m-%d %H:%M:%S.%f', 'comparison': True, 'unique': False},

        {'json_field': 'enddate', 'to_field': 'enddate', 'values_map': {'': None}, 'parent': '',
         'fixed_date': '%Y-%m-%d %H:%M:%S.%f', 'comparison': False, 'unique': False},

    ]


class SettingsImportAPI(SettingsImportBudget):
    """ Настройки парсера API. Наследуется от нужных настроек"""


