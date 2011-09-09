# -*- coding: utf-8 -*-

import utils

def config_context(request):
    return dict([(group._meta.name, group)
                 for group in utils.registry])
