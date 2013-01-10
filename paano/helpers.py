from flask import request, g, url_for as _url_for

from .constants import DEFAULT_LANG


def url_for(*args, **kwargs):
    """
    Override Flask's `url_for` to retain `lang` and `platform` params
    across requests
    """

    selected_lang = kwargs.get('lang', request.args.get('lang'))
    if selected_lang not in (None, DEFAULT_LANG):
        kwargs['lang'] = selected_lang

    selected_platform = kwargs.get('platform', request.args.get('platform'))
    if selected_platform not in (None, g.detected_platform):
        kwargs['platform'] = selected_platform

    return _url_for(*args, **kwargs)
