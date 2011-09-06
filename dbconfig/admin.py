# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.admin.options import csrf_protect_m
from django import template
from django.shortcuts import render_to_response, redirect

import models
import utils


class ConfigAdmin(admin.ModelAdmin):
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, instance=None):
        return instance is None
    
    has_delete_permission = has_change_permission
    
    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        valid = True
        forms = []
        for name, group_cls in utils.registry:
            if request.method == "POST":
                form = group_cls.Form(request.POST,
                                      initial=group_cls.form_initial)
                if not form.is_valid():
                    valid = False
            else:
                form = group_cls.Form(initial=group_cls.form_initial)
            forms.append({
                "cls":  group_cls,
                "name": group_cls.verbose_name,
                "form": form
            })
        if request.method == "POST" and valid:
            for form in forms:
                form["cls"].update(**form["form"].cleaned_data)
            self.message_user(request, u"Config values saved")
            return redirect(request.path)
        context = template.RequestContext(request, {"forms": forms})
        return render_to_response("admin/dbconfig_list.html", context)


if utils.registry:
    admin.site.register(models.DbConfigValue, ConfigAdmin)
