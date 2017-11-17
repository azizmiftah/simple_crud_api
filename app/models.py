# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

def password_validator(password):
	min_length = 6
	char_length = 1
	special_characters = "[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
	if len(password) < 6:
		raise ValidationError(_('Ensure this field has at least %(min_length)d characters.') % {'min_length': min_length})
	if not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
		raise ValidationError(_('Password must contain at least %(char_length)d digit and %(char_length)d letter.') % {'char_length': char_length})

class User(models.Model):
	name = models.CharField(max_length=200, blank=False, null=False)
	email = models.EmailField(null=False, unique=True)
	password = models.CharField(validators=[password_validator], max_length=500, blank=False, null=False)
	activate_code = models.CharField(max_length=50, blank=True, null=True)
	active = models.BooleanField(default=False)

class Article(models.Model):
	user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='%(class)s_user')
	title = models.CharField(max_length=200, blank=False, null=False)
	content = models.TextField(blank=True, null=False)
	created_at = models.DateTimeField(blank=True, null=True)




