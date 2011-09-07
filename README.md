dbconfig is easy to use app which stores user defined configs in database

usage:
======

add `dbconfig` to INSTALLED_APPS

turn on "admin autodiscover"

somewhere in your models

    from django import forms
    from dbconfig import ConfigGroup
    
    
    class NewsConfig(ConfigGroup):
        
        per_page = forms.IntegerField(label=u"How many news should we show on one page")
        hot = forms.ModelChoiceField(queryset=News.objects.all(),
                                     label=u"Show selected news on index page")
        
        verbose_name = "News config"


access value in code as `NewsConfig.per_page` (with dynamic getattr / setattr)
or with get / set functions as `NewsConfig.get_per_page()` and `NewsConfig.set_per_page(15)`

values will be cached in `dbconfig` cache backend if configured, or in locmem by default
