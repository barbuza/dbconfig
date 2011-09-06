# -*- coding: utf-8 -*-

import cPickle as Pickle
import base64

from django import forms

import models


registry = []


class ConfigManager(object):
    
    def __init__(self, name, fields):
        self._name = name
        self._fields = fields
    
    def __getattr__(self, name_):
        if name_.startswith("_"):
            return super(ConfigManager, self).__getattr__(name_)
        name = "%s.%s" % (self._name, name_)
        return models.DbConfigValue.objects.get_value_for(name)
    
    def __setattr__(self, name_, value):
        if name_.startswith("_"):
            return super(ConfigManager, self).__setattr__(name_, value)
        if name_ not in self._fields \
                or not isinstance(self._fields[name_], forms.Field):
            raise AttributeError(name_)
        name = "%s.%s" % (self._name, name_)
        models.DbConfigValue.objects.set_value_for(name, value)


class ConfigGroup(object):
    
    class __metaclass__(type):
        
        def __new__(cls, name, bases, attrs):
            if bases == (object, ):
                return type.__new__(cls, name, bases, attrs)
            attrs.update(config=ConfigManager(name, attrs))
            klass = type.__new__(cls, name, bases, attrs)
            if (name, klass) not in registry:
                registry.append((name, klass))
            return klass
    
    @classmethod
    def admin_form(cls):
        fields = {}
        cls_name = cls.__name__
        for name in dir(cls):
            value = getattr(cls, name)
            if isinstance(value, forms.Field):
                fields["%s.%s" % (cls_name, name)] = value
        return type("%sForm" % cls_name, (forms.Form, ), fields)
    
    @classmethod
    def values(cls):
        values = {}
        for name in dir(cls):
            if isinstance(getattr(cls, name), forms.Field):
                values[name] = getattr(cls.config, name)
        return values

