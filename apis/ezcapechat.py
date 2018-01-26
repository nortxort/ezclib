from util import web


class MissingFlashVarsError(Exception):
    """ Raised on missing flash vars. """
    pass


class CouldNotSetT2Error(Exception):
    """ Raised when setting t2 failed. """
    pass


class Params:
    """
    Class responsible for gathering the various connect parameters,
    needed before an connection can be made.
    """
    _base_url = u'https://www.ezcapechat.com/rooms/{0}'
    _t2_post_url = u'https://www.ezcapechat.com/php/ajax/join_room.php?n={0}'
    _html_source = u''

    def __init__(self, room_name, username, n_key=None, proxy=None):
        """
        Initialize the Params class.

        :param room_name: The room name.
        :type room_name: unicode
        :param username: The username.
        :type username: unicode
        :param n_key: n_key passed on from the login page.
        :type n_key: str
        :param proxy: Use a proxy for requests.
        :type proxy: str
        """
        self._room_name = room_name
        self._username = username
        self._provided_n_key = n_key
        self._proxy = proxy
        self._n_key = u''
        self._flash_vars = []
        self._t2 = u''

        page = web.get(url=self._base_url.format(self._room_name), proxy=self._proxy)
        if page.error is None:
            self._html_source = page.content
            self._set_n_key()
            self._set_flash_vars()
            self._set_t2()
        else:
            raise Exception('Something went wrong, page.error=%s' % page.error)

    @property
    def ip(self):
        """
        Rtmp Ip.

        NOTE: hardcoded in to the swf along with: 107.191.99.231:1935
        It does looks like these change at random(decompiled swf code)

        :return: The rtmp Ip.
        :rtype: str
        """
        return u'107.191.96.85'

    @property
    def port(self):
        """
        Rtmp Port.

        :return: Default rtmp port.
        :rtype: int
        """
        return 1935

    @property
    def tc_url(self):
        """
        Rtmp tcUrl.

        :return: The Rtmp tcUrl
        :rtype: str
        """
        return u'rtmp://{0}:{1}/chat/{2}'.format(self.ip, self.port, self._room_name)

    @property
    def app(self):
        """
        Rtmp App.

        :return: The Rtmp app.
        :rtype: str
        """
        return u'chat/%s' % self._room_name

    @property
    def swf_url(self):
        """
        Rtmp SwfUrl.

        :return: The Rtmp SwfUrl.
        :rtype: str
        """
        # maybe the *.swf can be parsed?
        return u'https://www.ezcapechat.com/chat26.swf/[[DYNAMIC]]/1'

    @property
    def page_url(self):
        """
        Rtmp PageUrl.

        :return: The Rtmp PageUrl
        :rtype:
        """
        return self._base_url.format(self._room_name)

    @property
    def t2(self):
        """
        Connect parameter t2 (SHA-256?) hash key.

        :return: T2 hash key.
        :rtype: str
        """
        return self._t2

    @property
    def n_key(self):
        """
        MD5 hash n_key.

        :return:
        :rtype:
        """
        return self._n_key

    @property
    def flash_vars(self):
        """
        The flash vars from the html source code.

        :return: The flash vars as a list.
        :rtype: list
        """
        return self._flash_vars

    @property
    def user_id(self):
        """
        The user ID (if any) extracted from the flash vars.

        :return: The user ID, or default 0
        :rtype: int
        """
        return int(self.flash_vars[2])

    @property
    def t1(self):
        """
        Connect parameter t1 (SHA-256?) hash key.

        :return: T1 hash key.
        :rtype: str
        """
        return self.flash_vars[5]

    @property
    def swf_id(self):
        """
        Swf id.

        :return: The swf id extracted from the flash vars.
        :rtype: str
        """
        return self.flash_vars[6]

    def _set_t2(self):
        """
        Set the t2 property value.

        TODO: Change to property setter. E.g @property.setter ?
        """
        if self.n_key is not None and self.t1 is not None:

            ts = int(web.time.time())
            post_url = self._t2_post_url.format(self.n_key)

            mpd = web.requests_toolbelt.MultipartEncoder(
                fields={
                    'room_name': self._room_name,
                    'user_id': u'%s' % self.user_id,
                    't1': self.t1,
                    'username': self._username
                },
                boundary='-------------------------%s' % ts  # 3106125133281
            )

            header = web.utils.CaseInsensitiveDict(data={
                'Accept-Language': 'en-US,en;q=0.5',
                'Content-Type': mpd.content_type
            })

            response = web.post(url=post_url, post_data=mpd, header=header,
                                referer=self._base_url.format(self._room_name), json=True, proxy=self._proxy)

            if 'error' not in response.json:
                if 't2' in response.json:
                    self._t2 = response.json['t2']
            else:
                raise CouldNotSetT2Error(response.json)
        else:
            raise CouldNotSetT2Error('n_key=%s, t1=%s' % (self.n_key, self.t1))

    def _set_n_key(self):
        """
        Set the n_key property value.

        TODO: Change to property setter. E.g @property.setter ?
        """
        if self._provided_n_key is not None:
            # further checks here? len() == 32
            self._n_key = self._provided_n_key
        else:
            if self._html_source:
                pattern = 'n = \''
                if pattern in self._html_source:
                    self._n_key = self._html_source.split(pattern)[1].split('\';')[0]

    def _set_flash_vars(self):
        """
        Set the flash_vars property value.

        TODO: Change to property setter. E.g @property.setter ?
        """
        if self._html_source:
            pattern = 'new _rmp('
            if pattern in self._html_source:
                _vars = self._html_source.split(pattern)[1].split(');')[0].split(',')
                for var in _vars:
                    self._flash_vars.append(var.replace('\'', ''))

        if len(self._flash_vars) < 7:
            raise MissingFlashVarsError('flash vars len: %s flash vars: %s' %
                                        (len(self._flash_vars), self._flash_vars))
