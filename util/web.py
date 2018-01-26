""" Web related functions and utilities. version 0.0.7 """
import time
import logging
import requests
import requests_toolbelt
import requests.utils as utils
import requests.structures as structures

__all__ = ['utils', 'requests_toolbelt', 'structures']

# Default user agent.
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0'

log = logging.getLogger(__name__)

__session = requests.session()


def is_cookie_expired(cookie_name):
    """
    Check if a session cookie is expired.

    :param cookie_name: The cookie name
    :type cookie_name: str
    :return: True if expired, False if not expired,
    or None if the cookie name is not in the session cookies.
    :rtype: bool
    """
    expires = int
    timestamp = int(time.time())

    for cookie in __session.cookies:
        if cookie.name == cookie_name:
            expires = cookie.expires
        else:
            return None

    if timestamp > expires:
        log.debug('cookie[\'%s\'] is expired. time stamp: %s, expires: %s' %
                  (cookie_name, timestamp, expires))
        return True

    log.debug('cookie[\'%s\'] is not expired. time stamp: %s, expires: %s' %
              (cookie_name, timestamp, expires))

    return False


def delete_cookie(cookie_name):
    """
    Delete a session cookie by name.

    :param cookie_name: The name of the cookie to delete.
    :type cookie_name: str
    :return: True if the cookie was deleted, else False.
    :rtype: bool
    """
    if cookie_name in __session.cookies:
        log.debug('session cookies before deletion: %s' % __session.cookies)
        del __session.cookies[cookie_name]
        log.debug('session cookies after deletion: %s' % __session.cookies)

        return True

    return False


def has_cookie(cookie_name):
    """
    Check if a cookie is in the session cookies.

    :param cookie_name: The name of the cookie to check.
    :type cookie_name: str
    :return: A request.cookie if the cookie is in session cookies, else False.
    :rtype: bool | requests.cookie
    """
    if cookie_name in __session.cookies:
        log.debug('cookie `%s` found in session.' % __session.cookies[cookie_name])
        return __session.cookies[cookie_name]

    log.debug('no cookie named `%s` found in session.' % cookie_name)
    return False


class Response:
    """ Class representing a response. """
    def __init__(self, content, json, cookies, headers, status_code, error=None):
        """
        Initiate the Response and set its values.
        """
        self.content = content
        self.json = json
        self.cookies = cookies
        self.headers = headers
        self.status_code = status_code
        self.error = error


def get(url, **options):
    json = options.get('json', False)
    proxy = options.get('proxy', u'')
    header = options.get('header', None)
    timeout = options.get('timeout', 20)
    referer = options.get('referer', None)
    session = options.get('session', True)

    default_header = utils.default_headers()
    default_header['User-Agent'] = USER_AGENT

    if referer is not None:
        default_header['Referer'] = referer

    if isinstance(header, structures.CaseInsensitiveDict):
        default_header.update(header)

    if proxy:
        _proxy = {
            'https': 'http://%s' % proxy,
            'http': 'http://%s' % proxy
        }
        proxy = _proxy

    _e = None
    _gr = None
    _json = None

    log.debug('url: %s' % url)
    try:
        if not session:
            _gr = requests.request(method='GET', url=url, headers=default_header, proxies=proxy, timeout=timeout)
        else:
            _gr = __session.request(method='GET', url=url, headers=default_header, proxies=proxy, timeout=timeout)
        if json:
            _json = _gr.json()
    except ValueError as ve:
        log.error('ValueError while decoding `%s` to json. %s' % (url, ve))
        _e = ve
    except (requests.ConnectionError, requests.RequestException) as re:
        log.error('requests exception: %s' % re)
        _e = re
    finally:
        if _gr is None or _e is not None:
            _response = Response(None, None, None, None, None, error=_e)
        else:
            _response = Response(_gr.text, _json, _gr.cookies, _gr.headers, _gr.status_code)

        return _response


def post(url, post_data, **options):
    json = options.get('json', False)
    proxy = options.get('proxy', u'')
    header = options.get('header', None)
    timeout = options.get('timeout', 20)
    referer = options.get('referer', None)
    stream = options.get('is_stream', False)
    redirect = options.get('follow_redirect', False)
    session = options.get('session', True)

    default_header = utils.default_headers()
    default_header['User-Agent'] = USER_AGENT

    if referer is not None:
        default_header['Referer'] = referer

    if isinstance(header, structures.CaseInsensitiveDict):
        default_header.update(header)

    if proxy:
        _proxy = {
            'https': 'http://%s' % proxy,
            'http': 'http://%s' % proxy
        }
        proxy = _proxy

    _e = None
    _pr = None
    _json = None

    log.debug('url: %s, post_data: %s' % (url, post_data))
    try:
        if not session:
            _pr = requests.request(method='POST', url=url, data=post_data, headers=default_header,
                                   allow_redirects=redirect, proxies=proxy, timeout=timeout, stream=stream)
        else:
            _pr = __session.request(method='POST', url=url, data=post_data, headers=default_header,
                                    allow_redirects=redirect, proxies=proxy, timeout=timeout, stream=stream)
        if json:
            _json = _pr.json()
    except ValueError as ve:
        log.error('ValueError while decoding `%s` to json. %s' % (url, ve))
        _e = ve
    except (requests.ConnectionError, requests.RequestException) as re:
        log.error('requests exception: %s' % re)
        _e = re
    finally:
        if _pr is None or _e is not None:
            _response = Response(None, None, None, None, None, error=_e)
        else:
            _response = Response(_pr.text, _json, _pr.cookies, _pr.headers, _pr.status_code)

        return _response
