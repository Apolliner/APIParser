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



[('Meta', <class 'ImportAPI.management.commands.parser.assembler_serializer.<locals>.MySerializer.Meta'>),
('__class__', <class 'rest_framework.serializers.SerializerMetaclass'>),
('__class_getitem__', <bound method BaseSerializer.__class_getitem__ of <class 'ImportAPI.management.commands.parser.assembler_serializer.<locals>.MySerializer'>>),
('__deepcopy__', <function Field.__deepcopy__ at 0x0000026F84965F70>),
('__delattr__', <slot wrapper '__delattr__' of 'object' objects>),

('__dict__', mappingproxy({
'__module__': 'ImportAPI.management.commands.parser', '__doc__': ' Базовый сериализатор',
'Meta': <class 'ImportAPI.management.commands.parser.assembler_serializer.<locals>.MySerializer.Meta'>,
'_declared_fields': OrderedDict(),
'budgtypecode': SerializerMethodField(source='budgettype'),
'enddate': SerializerMethodField(source='enddate'),

'get_parentcode': <bound method assembler_serializer.<locals>.fabric_get_parent_method.<locals>.get_base_parent of
<class 'ImportAPI.management.commands.parser.assembler_serializer.<locals>.MySerializer'>>,

'parentcode': SerializerMethodField()
})),
('__dir__', <method '__dir__' of 'object' objects>),
('__doc__', ' Базовый сериализатор'),
('__eq__', <slot wrapper '__eq__' of 'object' objects>),
('__format__', <method '__format__' of 'object' objects>),
('__ge__', <slot wrapper '__ge__' of 'object' objects>),
('__getattribute__', <slot wrapper '__getattribute__' of 'object' objects>),
('__getitem__', <function Serializer.__getitem__ at 0x0000026F8498DE50>),
('__gt__', <slot wrapper '__gt__' of 'object' objects>),
('__hash__', <slot wrapper '__hash__' of 'object' objects>),
('__init__', <function BaseSerializer.__init__ at 0x0000026F8497C670>),
('__init_subclass__', <built-in method __init_subclass__ of SerializerMetaclass object at 0x0000026F8403CB20>),
('__iter__', <function Serializer.__iter__ at 0x0000026F8498DDC0>),
('__le__', <slot wrapper '__le__' of 'object' objects>),
('__lt__', <slot wrapper '__lt__' of 'object' objects>),
('__module__', 'ImportAPI.management.commands.parser'),
('__ne__', <slot wrapper '__ne__' of 'object' objects>),
('__new__', <function BaseSerializer.__new__ at 0x0000026F8498AD30>),
('__reduce__', <method '__reduce__' of 'object' objects>),
('__reduce_ex__', <method '__reduce_ex__' of 'object' objects>),
('__repr__', <function Serializer.__repr__ at 0x0000026F8498DD30>),
('__setattr__', <slot wrapper '__setattr__' of 'object' objects>),
('__sizeof__', <method '__sizeof__' of 'object' objects>),
('__str__', <slot wrapper '__str__' of 'object' objects>),
('__subclasshook__', <built-in method __subclasshook__ of SerializerMetaclass object at 0x0000026F8403CB20>),
('__weakref__', <attribute '__weakref__' of 'Field' objects>),
('_creation_counter', 6),
('_declared_fields', OrderedDict()),
('_get_model_fields', <function ModelSerializer._get_model_fields at 0x0000026F8498F160>),
('_read_only_defaults', <function Serializer._read_only_defaults at 0x0000026F8498DA60>),
('_readable_fields', <property object at 0x0000026F8497FBD0>),
('_writable_fields', <property object at 0x0000026F8497F7C0>),
('bind', <function Field.bind at 0x0000026F849655E0>),
('budgtypecode', SerializerMethodField(source='budgettype')),
('build_field', <function ModelSerializer.build_field at 0x0000026F8498EB80>),
('build_nested_field', <function ModelSerializer.build_nested_field at 0x0000026F8498ED30>),
('build_property_field', <function ModelSerializer.build_property_field at 0x0000026F8498EDC0>),
('build_relational_field', <function ModelSerializer.build_relational_field at 0x0000026F8498ECA0>),
('build_standard_field', <function ModelSerializer.build_standard_field at 0x0000026F8498EC10>),
('build_unknown_field', <function ModelSerializer.build_unknown_field at 0x0000026F8498EEE0>),
('build_url_field', <function ModelSerializer.build_url_field at 0x0000026F8498EE50>),
('context', <property object at 0x0000026F8495EF40>),
('create', <function ModelSerializer.create at 0x0000026F8498E8B0>),
('data', <property object at 0x0000026F849859F0>),
('default_empty_html', <class 'rest_framework.fields.empty'>),
('default_error_messages', {'invalid': 'Invalid data. Expected a dictionary, but got {datatype}.'}),
('default_validators', []),
('enddate', SerializerMethodField(source='enddate')),
('errors', <property object at 0x0000026F84985A40>),
('fail', <function Field.fail at 0x0000026F84965D30>),
('fields', <django.utils.functional.cached_property object at 0x0000026F84981460>),
('get_attribute', <function Field.get_attribute at 0x0000026F84965940>),
('get_default', <function Field.get_default at 0x0000026F849659D0>),
('get_default_field_names', <function ModelSerializer.get_default_field_names at 0x0000026F8498EAF0>),
('get_extra_kwargs', <function ModelSerializer.get_extra_kwargs at 0x0000026F8498F040>),
('get_field_names', <function ModelSerializer.get_field_names at 0x0000026F8498EA60>),
('get_fields', <function ModelSerializer.get_fields at 0x0000026F8498E9D0>),
('get_initial', <function Serializer.get_initial at 0x0000026F8498D8B0>),
('get_parentcode', <bound method assembler_serializer.<locals>.fabric_get_parent_method.<locals>.get_base_parent of <class 'ImportAPI.management.commands.parser.assembler_serializer.<locals>.MySerializer'>>),
('get_unique_for_date_validators', <function ModelSerializer.get_unique_for_date_validators at 0x0000026F8498F310>),
('get_unique_together_validators', <function ModelSerializer.get_unique_together_validators at 0x0000026F8498F280>),
('get_uniqueness_extra_kwargs', <function ModelSerializer.get_uniqueness_extra_kwargs at 0x0000026F8498F0D0>),
('get_validators', <function ModelSerializer.get_validators at 0x0000026F8498F1F0>),
('get_value', <function Serializer.get_value at 0x0000026F8498D940>),
('include_extra_kwargs', <function ModelSerializer.include_extra_kwargs at 0x0000026F8498EF70>),
('initial', None), ('is_valid', <function BaseSerializer.is_valid at 0x0000026F8498D1F0>),
('many_init', <bound method BaseSerializer.many_init of <class 'ImportAPI.management.commands.parser.assembler_serializer.<locals>.MySerializer'>>),
('parentcode', SerializerMethodField()),
('root', <property object at 0x0000026F8495EEF0>),
('run_validation', <function Serializer.run_validation at 0x0000026F8498D9D0>),
('run_validators', <function Serializer.run_validators at 0x0000026F8498DAF0>),
('save', <function BaseSerializer.save at 0x0000026F8498D160>),
('serializer_choice_field', <class 'rest_framework.fields.ChoiceField'>),

('serializer_field_mapping', {
 <class 'django.db.models.fields.AutoField'>: <class 'rest_framework.fields.IntegerField'>,
<class 'django.db.models.fields.BigIntegerField'>: <class 'rest_framework.fields.IntegerField'>,
<class 'django.db.models.fields.BooleanField'>: <class 'rest_framework.fields.BooleanField'>,
<class 'django.db.models.fields.CharField'>: <class 'rest_framework.fields.CharField'>,
<class 'django.db.models.fields.CommaSeparatedIntegerField'>: <class 'rest_framework.fields.CharField'>,
<class 'django.db.models.fields.DateField'>: <class 'rest_framework.fields.DateField'>,
<class 'django.db.models.fields.DateTimeField'>: <class 'rest_framework.fields.DateTimeField'>,
<class 'django.db.models.fields.DecimalField'>: <class 'rest_framework.fields.DecimalField'>,
<class 'django.db.models.fields.DurationField'>: <class 'rest_framework.fields.DurationField'>,
<class 'django.db.models.fields.EmailField'>: <class 'rest_framework.fields.EmailField'>,
<class 'django.db.models.fields.Field'>: <class 'rest_framework.fields.ModelField'>,
<class 'django.db.models.fields.files.FileField'>: <class 'rest_framework.fields.FileField'>,
<class 'django.db.models.fields.FloatField'>: <class 'rest_framework.fields.FloatField'>,
<class 'django.db.models.fields.files.ImageField'>: <class 'rest_framework.fields.ImageField'>,
<class 'django.db.models.fields.IntegerField'>: <class 'rest_framework.fields.IntegerField'>,
<class 'django.db.models.fields.NullBooleanField'>: <class 'rest_framework.fields.BooleanField'>,
<class 'django.db.models.fields.PositiveIntegerField'>: <class 'rest_framework.fields.IntegerField'>,
<class 'django.db.models.fields.PositiveSmallIntegerField'>: <class 'rest_framework.fields.IntegerField'>,
<class 'django.db.models.fields.SlugField'>: <class 'rest_framework.fields.SlugField'>,
<class 'django.db.models.fields.SmallIntegerField'>: <class 'rest_framework.fields.IntegerField'>,
<class 'django.db.models.fields.TextField'>: <class 'rest_framework.fields.CharField'>,
<class 'django.db.models.fields.TimeField'>: <class 'rest_framework.fields.TimeField'>,
<class 'django.db.models.fields.URLField'>: <class 'rest_framework.fields.URLField'>,
<class 'django.db.models.fields.UUIDField'>: <class 'rest_framework.fields.UUIDField'>,
<class 'django.db.models.fields.GenericIPAddressField'>: <class 'rest_framework.fields.IPAddressField'>,
<class 'django.db.models.fields.FilePathField'>: <class 'rest_framework.fields.FilePathField'>,
<class 'django.db.models.fields.json.JSONField'>: <class 'rest_framework.fields.JSONField'>
}),

('serializer_related_field', <class 'rest_framework.relations.PrimaryKeyRelatedField'>),
('serializer_related_to_field', <class 'rest_framework.relations.SlugRelatedField'>),
('serializer_url_field', <class 'rest_framework.relations.HyperlinkedIdentityField'>),
('to_internal_value', <function Serializer.to_internal_value at 0x0000026F8498DB80>),
('to_representation', <function Serializer.to_representation at 0x0000026F8498DC10>),
('update', <function ModelSerializer.update at 0x0000026F8498E940>),
('url_field_name', None),
('validate', <function Serializer.validate at 0x0000026F8498DCA0>),
('validate_empty_values', <function Field.validate_empty_values at 0x0000026F84965A60>),
('validated_data', <property object at 0x0000026F8496EB80>),
('validators', <property object at 0x0000026F84966040>)]