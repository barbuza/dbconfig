dbconfig is easy to use app which stores user defined configs in database

`0.3.0` version is python3 only (too lazy to mantain python2 compatibility)

usage:
======

add `dbconfig` to INSTALLED_APPS

turn on "admin autodiscover"

create `config.py` file in your app (near `models.py`)

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

files will be stored in `conf` directory under your `MEDIA_ROOT` with default storage,
they will be represented as `dbconfig.ConfigFile` which has `name`, `path` and `url` properties

model instances will be stored as pair of content type id and instance id, so you will not
have serialized model instances in database or cache

there is `dbconfig.config_context` context processor, it will populate context will all available
config group subclasses

remember that `dbconfig.autodiscover()` should be used before `admin.autodiscover()`
(if you want to place your ConfigGroup subclasses in %appname%.config modules)

configure your cache backends

    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "default",
        },
        "dbconfig": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "dbconfig",        
        },
    }

