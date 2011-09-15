# -*- coding: utf-8 -*-

from django import forms

import models


__all__ = ("registry", "ConfigGroup", "autodiscover", )


registry = []


def autodiscover():
    for models_module in models.get_apps():
        app_name = models_module.__name__.rsplit(".", 1)[0]
        conf_module = "%s.config" % app_name
        try:
            __import__(conf_module)
        except ImportError, err:
            if str(err) != "No module named config":
                raise


class ConfigManager(object):
    
    def __init__(self, name, fields):
        self.__dict__.update(_name=name, _fields=fields)
    
    def __getattr__(self, name):
        if name not in self._fields:
            raise AttributeError(name)
        field_name = "%s.%s" % (self._name, name)
        return models.DbConfigValue.objects.get_value_for(field_name)
    
    def __setattr__(self, name, value):
        if name not in self._fields \
                or not isinstance(self._fields[name], forms.Field):
            raise AttributeError(name)
        field_name = "%s.%s" % (self._name, name)
        models.DbConfigValue.objects.set_value_for(field_name, value)


class ConfigGroupMeta(object):
    
    def update(self, **kwargs):
        for name, value in kwargs.items():
            if name.startswith("%s." % self.name):
                name = name[len(self.name) + 1:]
            setattr(self.config_manager, name, value)
    
    @property
    def keys(self):
        return self.fields.keys()
    
    @property
    def values(self):
        res = {}
        for name in self.keys:
            res[name] = getattr(self.config_manager, name)
        return res
    
    @property
    def form_initial(self):
        res = {}
        for name in self.keys:
            field_name = "%s.%s" % (self.name, name)
            res[field_name] = getattr(self.config_manager, name)
        return res


class StaticProperty(object):
    
    def __init__(self, name):
        self.name = name
    
    def __get__(self, owner, cls):
        return getattr(cls._meta.config_manager, self.name)


class ConfigGroup(object):
    
    class __metaclass__(type):
        
        def __new__(self, name, bases, attrs):
            
            # skip all magic for ConfigGroup class itself
            if bases == (object, ):
                return type.__new__(self, name, bases, attrs)
            
            # pop all form fields from subclass to move them
            # into "Meta" class and create a "Form" class
            fields = {}
            for key in attrs.keys():
                if isinstance(attrs[key], forms.Field):
                    fields[key] = attrs.pop(key)
            
            # config manager will be used to get / set values
            config_manager = ConfigManager(name, fields)
            
            # "Form" class is created based on fields definitions
            # fields will contain subclass name as prefix to allow
            # multiple forms usage on same page without creating
            # boring formsets
            form_attrs = {}
            for field_name, field in fields.items():
                form_attrs["%s.%s" % (name, field_name)] = field
            form = type(name + "Form", (forms.Form, ), form_attrs)
            
            # "Meta" class will hold fields definition, manager
            # instance and "Form" class
            meta_attrs = {
                "name": name,
                "config_manager": config_manager,
                "form_class": form,
                "fields": fields
            }
            meta = type(name + "Meta", (ConfigGroupMeta, ), meta_attrs)()
            
            def create_getter(field_name):
                getter = lambda: getattr(config_manager, field_name)
                getter.__name__ = "%s.get_%s" % (name, field_name)
                return staticmethod(getter)
            
            def create_setter(field_name):
                setter = lambda val: setattr(config_manager, field_name, val)
                setter.__name__ = "%s.set_%s" % (name, field_name)
                return staticmethod(setter)
            
            # define getter / setter functions for all fields
            for field_name in fields:
                attrs.update({
                    field_name: StaticProperty(field_name),
                    "get_%s" % field_name: create_getter(field_name),
                    "set_%s" % field_name: create_setter(field_name),
                })
            
            attrs.update(_meta=meta)
            klass = type.__new__(self, name, bases, attrs)
            
            # we register subclass in a list to automatically display
            # all config forms on admin page
            if klass not in registry:
                registry.append(klass)
            
            return klass
        
        # setattr is passed to config manager instance
        def __setattr__(self, name, value):
            return setattr(self._meta.config_manager, name, value)
