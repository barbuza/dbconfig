dbconfig is easy to use app which stores user defined configs in database

usage:
======

add `dbconfig` to INSTALLED_APPS
turn on "admin autodiscover"
somewhere in your models

    from dbconfig import ConfigGroup
    
    class NewsConfig(ConfigGroup):
        
        per_page = int
        _per_page_help = u"How many news should we show on one page"
        
        verbose_name = "News config"

