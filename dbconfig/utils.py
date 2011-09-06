# -*- coding: utf-8 -*-

from django import forms

import models


registry = []


class cached_property(object):
    
    def __init__(self, method, name=None):
        self.method = method
        self.name = name or method.__name__
        self.__doc__ = method.__doc__
    
    def __get__(self, inst, cls):
        if inst is None:
            return self
        result = self.method(inst)
        setattr(inst, self.name, result)
        return result


class ConfigManager(object):
    
    def __init__(self, name, fields):
        self._name = name
        self._fields = fields
    
    def __getattr__(self, name):
        if name.startswith("_"):
            return super(ConfigManager, self).__getattr__(name)
        field_name = "%s.%s" % (self._name, name)
        return models.DbConfigValue.objects.get_value_for(field_name)
    
    def __setattr__(self, name, value):
        if name.startswith("_"):
            return super(ConfigManager, self).__setattr__(name, value)
        if name not in self._fields \
                or not isinstance(self._fields[name], forms.Field):
            raise AttributeError(name)
        field_name = "%s.%s" % (self._name, name)
        models.DbConfigValue.objects.set_value_for(field_name, value)


class ConfigGroup(object):
    
    class __metaclass__(type):
        
        def __new__(self, name, bases, attrs):
            if bases == (object, ):
                return type.__new__(self, name, bases, attrs)
            attrs.update(config=ConfigManager(name, attrs))
            klass = type.__new__(self, name, bases, attrs)
            if (name, klass) not in registry:
                registry.append((name, klass))
            return klass
        
        def update(self, **kwargs):
            for name, value in kwargs.items():
                if name.startswith("%s." % self.__name__):
                    name = name[len(self.__name__) + 1:]
                setattr(self.config, name, value)
        
        @property
        def keys(self):
            keys = []
            for name in dir(self):
                if isinstance(getattr(self, name), forms.Field):
                    keys.append(name)
            return keys
        
        @property
        def values(self):
            res = {}
            for name in self.keys:
                res[name] = getattr(self.config, name)
            return res
        
        @cached_property
        def Form(self):
            fields = {}
            for name in self.keys:
                fields["%s.%s" % (self.__name__, name)] = getattr(self, name)
            klass = type("%sForm" % self.__name__, (forms.Form, ), fields)
            klass.__module__ = self.__module__
            return klass
        
        @property
        def form_initial(self):
            res = {}
            for name in self.keys:
                field_name = "%s.%s" % (self.__name__, name)
                res[field_name] = getattr(self.config, name)
            return res
