# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.admin.options import csrf_protect_m
from django import template
from django.shortcuts import render_to_response, redirect

import models


class ConfigAdmin(admin.ModelAdmin):
    
    def has_add_permission(self, request):
        return False
    
    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        valid = True
        forms = []
        for name, cls in models.registry:
            form_cls = cls.admin_form()
            if request.method == "POST":
                form = form_cls(request.POST)
                if not form.is_valid():
                    valid = False
            else:
                form = form_cls()
            forms.append({
                "cls": cls,
                "name": cls.verbose_name,
                "form": form
            })
        if request.method == "POST" and valid:
            for form in forms:
                for name, value in form["form"].cleaned_data.items():
                    name = name.split(".")[1]
                    setattr(form["cls"].config, name, value)
            self.message_user(request, u"Config values saved")
            return redirect(request.path)
        context = template.RequestContext(request, {"forms": forms})
        return render_to_response("admin/dbconfig_list.html", context)


if models.registry:
    admin.site.register(models.DbConfigValue, ConfigAdmin)
