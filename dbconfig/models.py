# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django import forms
from django.utils import simplejson as json

registry = []


class DbConfigValue(models.Model):
    
    name = models.CharField(max_length=255, primary_key=True)
    json_value = models.TextField()
    
    class Meta:
        verbose_name = "Config"
        verbose_name_plural = "Config"


class ConfigManager(object):
    
    def __init__(self, name, fields):
        self._name = name
        self._cache = {}
        self._fields = fields
    
    def __getattr__(self, name_):
        if name_.startswith("_"):
            return super(ConfigManager, self).__getattr__(name_)
        name = "%s.%s" % (self._name, name_)
        if name in self._cache:
            return self._cache[name]
        try:
            db_value = DbConfigValue.objects.get(name=name)
            value = json.loads(db_value.json_value)
            if self._fields[name_]["type"] is datetime.datetime:
                value = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            elif self._fields[name_]["type"] is datetime.date:
                value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
            self._cache[name] = value
            return value
        except DbConfigValue.DoesNotExist:
            return None
    
    def __setattr__(self, name_, value):
        if name_.startswith("_"):
            return super(ConfigManager, self).__setattr__(name_, value)
        if name_ not in self._fields:
            raise AttributeError(name_)
        if type(value) is not self._fields[name_]["type"]:
            raise ValueError("value is not %s" % self._fields[name_]["type"])
        name = "%s.%s" % (self._name, name_)
        try:
            db_value = DbConfigValue.objects.get(name=name)
        except DbConfigValue.DoesNotExist:
            db_value = DbConfigValue(name=name)
        self._cache[name] = value
        if self._fields[name_]["type"] in (datetime.datetime, datetime.date):
            value = value.isoformat()
        db_value.json_value = json.dumps(value)
        db_value.save()
        return value


class ConfigGroup(object):
    
    class __metaclass__(type):
        
        def __new__(cls, name, bases, attrs):
            if bases == (object, ):
                return type.__new__(cls, name, bases, attrs)
            fields = {}
            for key, value in attrs.items():
                if value in (int, float, str, unicode, bool, datetime.date,
                             datetime.datetime):
                    fields[key] = {
                        "type": value,
                        "label": attrs.get("_%s_help" % key, key)
                    }
            manager = ConfigManager(name, fields)
            klass = type.__new__(cls, name, bases,
                {"_fields": fields, "config": manager,
                 "verbose_name": attrs.get("verbose_name", name)})
            if (name, klass) not in registry:
                registry.append((name, klass))
            return klass
    
    @classmethod
    def admin_form(cls):
        fields = {}
        cls_name = cls.__name__
        for name, cfg in cls._fields.items():
            type_ = cfg["type"]
            label = cfg["label"]
            val = getattr(cls.config, name)
            if type_ is int:
                field = forms.IntegerField(label=label, initial=val)
            elif type_ in (str, unicode):
                field = forms.CharField(label=label, initial=val)
            elif type_ is datetime.date:
                field = forms.DateField(label=label, initial=val)
            elif type_ is datetime.datetime:
                field = forms.DateTimeField(label=label, initial=val)
            elif type_ is bool:
                field = forms.BooleanField(label=label, required=False, initial=val)
            fields["%s.%s" % (cls_name, name)] = field
        return type("%sForm" % cls_name, (forms.Form, ), fields)

