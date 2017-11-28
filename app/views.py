# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import jwt
from django.conf import settings
from models import *
from serializers import *
from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import exceptions
from rest_framework.response import Response
from django.core.mail import EmailMessage
import random, string
from datetime import datetime

def get_user_from_token(request):
	try:
		token = str(request.META['HTTP_AUTHORIZATION'])
	except:
		token = str(request.META['HTTP_API_KEY'])
	payload = jwt.decode(token, settings.SECRET_KEY)
	user = User.objects.filter(id=payload['id']).first()
	return user

class TokenPermission(permissions.BasePermission):
	"""
	Global permission check.
	"""
	def has_permission(self, request, view):
		auth = ''
		try:
			auth = request.META['HTTP_AUTHORIZATION']
		except Exception as e:
			try:
				auth = request.META.get('HTTP_API_KEY', '')
			except Exception as e:
				msg = (str(e))
				raise exceptions.AuthenticationFailed(msg)
		if auth:
			try:
				token = str(auth)
				payload = jwt.decode(token, settings.SECRET_KEY)
				user = User.objects.filter(id=payload['id'], email__iexact=payload['email']).first()
				if user:
					if not user.active:
						msg = ('User with authentication credentials were not activated.')
						raise exceptions.AuthenticationFailed(msg)
				return user is not None
			except jwt.ExpiredSignature:
				msg = ('Signature has expired.')
				raise exceptions.AuthenticationFailed(msg)
			except jwt.DecodeError:
				msg = ('Error decoding signature.')
				raise exceptions.AuthenticationFailed(msg)
			except IndexError as e:
				# msg = ('Authentication credentials were not provided.' + str(e.message))
				msg = ('Authentication credentials were not provided. index error')
				raise exceptions.AuthenticationFailed(msg)
		else:
			msg = ('Authentication credentials were not provided')
			raise exceptions.AuthenticationFailed(msg)


def send_mail(to=[], title='', body=''):
	email = EmailMessage(title, body, to=to)
	return email.send()

class ObtainTokenView(APIView):

	serializer_class=ParamObtainToken
	
	def post(self, request):
		email = request.data.get("email")
		password = request.data.get("password")
		errors = {}
		if not email:
			errors["email"] = ["This field is required"]
		if not password:
			errors["password"] = ["This field is required"]
		if errors:
			return Response({"res":0, 'Message':'Wrong authentication.', 'detail':errors}, 400)

		user = User.objects.filter(email=request.data['email']).first()
		if not user:
			return Response({"res":0, 'Message':"User Doesn't exist."}, 400)
		elif not user.active:
			return Response({"res":0, 'Message':"User Doesn't active."}, 400)

		if not check_password(password=password, encoded=user.password):
			return Response({'res':0,'Message':'Wrong authentication.'}, 400)

		payload = {'id':user.id, 'email':user.email}
		token = jwt.encode(payload, settings.SECRET_KEY)
		return Response({"res":1,"message":"OK","token":token, "user": UserSerial(user).data})

class CheckEmailView(APIView):

	serializer_class = CheckEmailSerial

	def get(self, request):
		if not 'email' in request.GET:
			return Response({'result':None,"detail":{'email':["This field is required."]}});
		if not User.objects.filter(email__iexact=request.GET['email']):
			return Response({'result':None,"detail":"Email is available."});
		return Response({'result':None,"detail":"Email has already taken."});

class RegisterView(APIView):

	serializer_class = UserSerial

	def post(self, request):
		serial = UserSerial(data=request.data)
		if serial.is_valid():
			code = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(30))
			send_mail(to=[serial.validated_data['email']], title='Simple CRUD Account Info', body='click this activation link: ' + "http://localhost/tugas_ptbig/activation.php?activation_code=" + code)
			serial.save(activate_code=code, password=make_password(password=request.data['password'], salt=None), active=False)
			return Response({"result":serial.data,"message":"OK"})
		return Response({"result":None,"detail":serial.errors}, 400)

class ActivateView(APIView):

	# permission_classes = (TokenPermission,)

	def get(self, request):
		code = request.GET.get('activation_code')
		result = User.objects.filter(activate_code=code).update(active=True)
		if result == 1:
			return Response({"result":True, "message":"User has been activated"}, 200)
		return Response({"result":False, "message":"Activation code is invalid"}, 400)

class UserView(APIView):

	serializer_class = UserSerial
	permission_classes = (TokenPermission,)

	def get(self, request, id=None):
		if id:
			user = User.objects.filter(id=id)
		else:
			user = User.objects.all()
		serial = UserSerial(user, many=True)
		return Response({"result":serial.data,"message":"OK"})

	def put(self, request, id=None):
		if id:
			user = User.objects.filter(id=id).first()
			if not user:
				return Response({"result":None,"message":"Nothing updated", "detail":{"id":["Does not exist"]}})
			serial = UserSerial(user, data=request.data, partial=True)
			if serial.is_valid():
				serial.save()
				return Response({"result":serial.data,"message":"OK"})
			return Response({"result":None,"message":"Failed", "detail":serial.errors}, 400)
		return Response({"result":None,"message":"Failed", "detail": "Method \"PUT\" not allowed."})

	def delete(self, request, id=None):
		if id:
			result = User.objects.filter(id=id).delete()
			return Response({"result":result[0],"message":"OK", "detail":None})
		return Response({"result":None,"message":"Failed", "detail": "Method \"DELETE\" not allowed."}, 403)

class ArticleView(APIView):

	serializer_class = ArticleSerial
	permission_classes = (TokenPermission,)

	def get(self, request, id=None):
		user = get_user_from_token(request)
		if id:
			article = Article.objects.filter(id=id, user=user)
		else:
			article = Article.objects.filter(user=user)
		serial = ArticleSerial(article, many=True)
		return Response({"result":serial.data,"message":"OK"})

	def post(self, request):
		user = get_user_from_token(request)
		serial = ArticleSerial(data=request.data)
		if serial.is_valid():
			serial.save(user=user, created_at=datetime.now())
			return Response({"result":serial.data,"message":"OK"})
		return Response({"result":None,"detail":serial.errors}, 400)

	def put(self, request, id=None):
		user = get_user_from_token(request)
		if id:
			article = Article.objects.filter(id=id, user=user).first()
			if not article:
				return Response({"result":None,"message":"Nothing updated", "detail":{"id":["Does not exist"]}})
			serial = ArticleSerial(article, data=request.data, partial=True)
			if serial.is_valid():
				serial.save()
				return Response({"result":serial.data,"message":"OK"})
			return Response({"result":None,"message":"Failed", "detail":serial.errors}, 400)
		return Response({"result":None,"message":"Failed", "detail": "Method \"PUT\" not allowed."})

	def delete(self, request, id=None):
		user = get_user_from_token(request)
		if id:
			result = Article.objects.filter(id=id, user=user).delete()
			return Response({"result":result[0],"message":"OK", "detail":None})
		return Response({"result":None,"message":"Failed", "detail": "Method \"DELETE\" not allowed."}, 403)
