# -*- coding: utf-8 -*-

import base64
import cPickle
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist


__all__ = ("DbConfigValue", "Model", )


Model = models.Model


class ModelReference(object):
    
    def __init__(self, instance):
        ctype = ContentType.objects.get_for_model(type(instance))
        self.ctype = ctype.pk
        self.pk = instance.pk
    
    def get_instance(self):
        try:
            ctype = ContentType.objects.get_for_id(self.ctype)
            return ctype.get_object_for_this_type(pk=self.pk)
        except ObjectDoesNotExist:
            return None


class DbConfigValueManager(models.Manager):
    
    def __init__(self):
        super(DbConfigValueManager, self).__init__()
        self._cache = {}
    
    def get_value_for(self, name):
        if name in self._cache:
            value = self._cache[name]
            if isinstance(value, ModelReference):
                value = value.get_instance()
            return value
        try:
            db_value = self.get(name=name)
            value = db_value.get_value()
            self._cache[name] = value
            if isinstance(value, ModelReference):
                value = value.get_instance()
            return value
        except ObjectDoesNotExist:
            return None
    
    def set_value_for(self, name, value):
        if isinstance(value, models.Model):
            value = ModelReference(value)
        self._cache[name] = value
        try:
            db_value = self.get(name=name)
        except ObjectDoesNotExist:
            db_value = DbConfigValue(name=name)
        db_value.value = value
        db_value.save()


class DbConfigValue(models.Model):
    
    name = models.CharField(max_length=255, primary_key=True)
    value64 = models.TextField()
    
    def get_value(self):
        pickled = base64.decodestring(self.value64)
        value = cPickle.loads(pickled)
        return value
    
    def set_value(self, value):
        pickled = cPickle.dumps(value, protocol=2)
        self.value64 = base64.encodestring(pickled)
        return value
    
    value = property(get_value, set_value)
    
    objects = DbConfigValueManager()
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = "Config"
        verbose_name_plural = "Config"
