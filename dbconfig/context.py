# -*- coding: utf-8 -*-

import utils

def config_context(request):
    return dict([(group.__name__, group)
                 for group in utils.registry])
