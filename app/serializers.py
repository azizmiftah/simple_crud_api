from rest_framework import serializers
from models import *

class UserSerial(serializers.ModelSerializer):
	class Meta:
		model = User
		# exclude = ('password',)
		depth = 1
		fields = '__all__'

class ArticleSerial(serializers.ModelSerializer):
	class Meta:
		model = Article
		depth = 1
		fields = '__all__'

class ParamObtainToken(serializers.ModelSerializer):
	class Meta:
		model = User
		exclude = ('name', 'activate_code', 'id')
