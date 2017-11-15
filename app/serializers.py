from rest_framework import serializers
from models import *

class UserSerial(serializers.ModelSerializer):
	class Meta:
		model = User
		# exclude = ('password',)
		depth = 1
		fields = '__all__'
