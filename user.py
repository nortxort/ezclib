
class Client:
    """ Class representing the client. """
    def __init__(self, nick):
        self.nick = u'' + nick
        self.key = u''
        self.join_time = 0
        self.ml = 0
        self.id = 0
        self.su = 0
        self.st = u''

    @property
    def is_mod(self):
        """
        Is client mod.

        :return: True if the client is moderator.
        :rtype: bool
        """
        if self.ml >= 100:
            return True
        return False

    @property
    def is_super(self):
        """
        Is the client a super.

        :return: True if the client is a super.
        :rtype: bool
        """
        if self.ml == 150:
            return True
        return False

    @property
    def is_owner(self):
        """
        Is the client owner of the room.

        :return: True if the client is owner of the room.
        :rtype: bool
        """
        if self.ml == 200:
            return True
        return False

    def add_data(self, **data):
        """
        Add data to the Client object.

        :param data: The dictionary Client data.
        :type data: dict
        """
        self.ml = data.get('ml', 0)      # mod level
        self.id = data.get('id', 0)      # ezcapechat user id (if logged in)
        self.su = data.get('su', 0)      # ?
        self.st = data.get('st')         # status related


class User:
    """ Class representing a user. """
    def __init__(self, **data):
        self.ml = data.get('ml', 0)      # mod level
        self.nick = data.get('un', '')   # nick
        self.id = data.get('id', 0)      # ezcapechat user id (if logged in)
        self.su = data.get('su', 0)      # ?
        self.st = data.get('st')         # status related

    @property
    def is_mod(self):
        """
        Is the user a mod.

        :return: True if the user is a mod.
        :rtype: bool
        """
        if self.ml >= 100:
            return True
        return False

    @property
    def is_super(self):
        """
        Is the user a super.

        :return: True if the user is super.
        :rtype: bool
        """
        if self.ml == 150:
            return True
        return False

    @property
    def is_owner(self):
        """
        Is the user owner of the room.

        :return: True if user is owner of the room.
        :rtype: bool
        """
        if self.ml == 200:
            return True
        return False


class Users:
    """ Class for doing various client/user related operations. """
    def __init__(self):
        self._users = dict()
        self._client = Client

    @property
    def client(self):
        """
        Returns the instance Client object.

        :return: Returns the Client object.
        :rtype: Client
        """
        return self._client

    @property
    def all(self):
        """
        Return a dictionary of all the users.

        :return: A dictionary containing all the User objects.
        :rtype: dict
        """
        return self._users

    @property
    def mods(self):
        """
        Returns a list of all the mods in the room.

        :return:
        :rtype:
        """
        _mods = []
        for username in self.all:
            if self.all[username].is_mod:
                _mods.append(self.all[username])
        return _mods

    @property
    def supers(self):
        """
        Return a list of all the supers in the room.

        :return:
        :rtype:
        """
        _supers = []
        for username in self.all:
            if self.all[username].is_super:
                _supers.append(self.all[username])
        return _supers

    def add_client(self, nick):
        """
        Initiate the Client class.

        :param nick:
        :type nick:
        """
        self._client = Client(nick)

    def add_client_data(self, data):
        """
        Add data to the Client object.

        :param data: The client data as a dictionary.
        :type data: dict
        """
        self._client.add_data(**data)

    def add(self, nick, user_data):
        """
        Add a user to the user to the user dictionary.

        :param nick: The nick of the user.
        :type nick: str
        :param user_data: Data containing info about the user.
        :type user_data: dict
        :return: User if the user nick was not in the user dictionary, else None.
        :rtype: User | None
        """
        if nick not in self._users:
            self._users[nick] = User(**user_data)
            return self._users[nick]
        return None

    def remove(self, nick):
        """
        Remove a user from the user dictionary.

        :param nick: The nick of the user to be removed.
        :type nick: str
        :return: The deleted user if deleted, else None
        :rtype: User | None
        """
        if nick in self._users:
            deleted_user = self._users[nick]
            del self._users[nick]
            return deleted_user
        return None

    def search(self, nick):
        """
        Search the user dictionary
        for a user matching the nick.

        :param nick: The nick of the user to search for.
        :type nick: str
        :return: The user if found, else None
        :rtype: User | None
        """
        if nick in self._users:
            return self._users[nick]
        return None
