# -*- coding: utf-8 -*-

import utils


__all__ = ("config_context", )


def config_context(request):
    return dict([(group._meta.name, group)
                 for group in utils.registry])
