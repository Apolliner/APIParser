from rest_framework import serializers
from .models import Budget

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        #fields = ('code', 'name', 'parentcode', 'startdate', 'enddate', 'status', 'budgettype')
        fields = '__all__'

