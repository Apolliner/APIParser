
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