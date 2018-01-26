import logging
import util.web


log = logging.getLogger(__name__)


class Account:
    """
    Account class responsible for account related operations.
    """
    _login_page_url = 'https://www.ezcapechat.com/login'
    _login_post_url = 'https://www.ezcapechat.com/php/go/go_login.php'
    _html_source = u''
    _n_key = u''

    def __init__(self, email, password, proxy=None):
        """
        Initialize the Account class.

        :param email: Login email.
        :type email: str
        :param password: Login password.
        :type password: str
        :param proxy: Use a proxy for the requests.
        :type proxy: str
        """
        self._email = u'' + email
        self._password = u'' + password
        self._proxy = proxy

        response = util.web.get(url=self._login_page_url, proxy=self._proxy)
        if response.error is None:
            self._html_source = response.content
            self._set_n_key()

    @property
    def n_key(self):
        """
        The n_key MD5 hash key.

        :return: MD5 hash key.
        :rtype: str
        """
        return self._n_key

    @property
    def is_logged_in(self):
        """
        Login check.

        :return: True if logged in, else False.
        :rtype: bool
        """
        if self._html_source is None:
            return False
        else:
            if '/manage?p=profile' in self._html_source:
                return True
            return False

    def login(self):
        """
        Login to an account, with the provided credentials(email, password).
        """
        if self._email and self._password:
            form_data = {
                'n': self.n_key,
                'email': self._email,
                'pass': self._password,
                'submit': 'Login: undefined'
            }

            log.debug('login form_data: %s' % form_data)
            response = util.web.post(url=self._login_post_url, post_data=form_data,
                                     referer=self._login_page_url, follow_redirect=True, proxy=self._proxy)
            log.debug('login response: %s' % response)
            if response.error is None:
                self._html_source = response.content
                self._set_n_key()

    def _set_n_key(self):
        """
        Set the n_key property value.

        TODO: Change to property setter instead. E.g @property.setter ?
        """
        pattern = 'n = \''
        if pattern in self._html_source:
            self._n_key = self._html_source.split(pattern)[1].split('\';')[0]
