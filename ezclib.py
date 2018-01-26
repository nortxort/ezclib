""" Ezcapechat RTMP library by Nortxort (https://github.com/nortxort) """
import json
import logging
import time

import config
from apis import ezcapechat
from pages import acc
from util import string_util
from rtmplib import rtmp

__version__ = '1.0.0'
log = logging.getLogger(__name__)
CONFIG = config


class EzcapechatRTMPProtocol:
    """
    Ezcapechat RTMP protocol.

    Contains event methods in use by the flash application.
    """
    def __init__(self, room_name, username, email=None, password=None, proxy=None):
        """
        Initialize the ezcapechat protocol class.

        :param room_name: The room name.
        :type room_name: str
        :param username: A user name.
        :type username: str
        :param email: Login email.
        :type email: str
        :param password: Login password.
        :type password: str
        :param proxy: Use a proxy.
        :type proxy: str
        """
        self.room_name = u'' + room_name
        self.username = u'' + username
        self.email = email
        self.password = password
        self.proxy = proxy

        self.connection = None
        self.is_connected = False
        self.client_id = 0

        self._pub_n_key = None
        self._room_id = 0
        self._msg_key = u''
        self._msg_counter = 1

    def _reset(self):
        """

        """
        self.username = u''
        self.client_id = 0
        self._pub_n_key = None  # consider this
        self._room_id = 0
        self._msg_key = u''
        self._msg_counter = 1

    def login(self):
        """
        Login to ezcapechat using the provided credentials.

        :return: True if logged in, else False.
        :rtype: bool
        """
        account = acc.Account(self.email, self.password)
        if self.email and self.password:
            if account.is_logged_in:
                self._pub_n_key = account.n_key
                return True
            account.login()
            self._pub_n_key = account.n_key
            return account.is_logged_in
        return False

    def connect(self):
        """ Connect to the remote server. """
        _error = None

        if not self.username.strip():
            self.username = string_util.create_random_string(6, 25)  # adjust length

        try:
            params = ezcapechat.Params(self.room_name, self.username,
                                       n_key=self._pub_n_key, proxy=self.proxy)

            self.connection = rtmp.RtmpClient(
                ip=params.ip,
                port=params.port,
                tc_url=params.tc_url,
                app=params.app,
                swf_url=params.swf_url,
                page_url=params.page_url,
                proxy=self.proxy,
                is_win=True
            )

            self.connection.connect(
                [
                    u'connect',             # custom connect string?
                    u'',                    # ?
                    params.t1,              # t1
                    params.t2,              # t2
                    0,                      # ?
                    u'',                    # ?
                    u'',                    # ?
                    u'',                    # ?
                    self.room_name,         # room name
                                            # value of guid (Shared Local Object)
                    u'A62E0786-7113-2F6F-9C14-6602B02F1872-A7F34D64-C322-314C-642F-B045CF448907',
                                            # ?
                    u'68F234E8-4070-59B7-0D9A-CAE4A8D33539-1BFE74C1-C98E-2834-3A85-BFA16CF4C032',
                    u'0.33',                # protocol version
                    u'',                    # room password
                    u'',                    # ?
                    False                   # disabled(flash_vars[0]) ?
                ]
            )
        except Exception as e:
            log.critical(e, exc_info=True)
            _error = e
        finally:
            if _error is not None:
                print ('connect error: %s' % _error)
            else:
                self.is_connected = True
                self.__callback()

    def disconnect(self):
        """ Disconnect from the remote server. """
        _error = None
        try:
            self.connection.shutdown()
        except Exception as e:
            log.error(e, exc_info=True)
            _error = 'disconnect error: %s' % e
        finally:
            if _error is not None and config.DEBUG_TO_CONSOLE:
                print (_error)
            self.is_connected = False
            self.connection = None

    def reconnect(self):
        """ Reconnect to the remote server. """
        if self.is_connected:
            self.disconnect()
        self._reset()
        time.sleep(config.RECONNECT_DELAY)  # increase reconnect delay?
        self.connect()

    def __callback(self):
        """ Callback loop reading packets/events from the stream. """

        log.debug('starting __callback loop, is_connected: %s' % self.is_connected)
        fails = 0

        while self.is_connected:
            try:
                amf_data = self.connection.amf()
                msg_type = amf_data['msg']
            except Exception as e:
                fails += 1
                print ('__callback error(%s): %s' % (fails, e))
                if fails == 2:
                    self.reconnect()
                    break
            else:
                fails = 0

                if config.DEBUG_TO_FILE:
                    log.debug(amf_data)

                if config.DEBUG_TO_CONSOLE:
                    print (amf_data)

                if msg_type == rtmp.rtmp_type.DT_COMMAND:

                    event_data = amf_data['command']
                    event = event_data[0]

                    if event == '_result':
                        self.on_result(event_data[3])

                    elif event == 'joinData':
                        self.on_join_data(event_data)

                    elif event == 'joinuser':
                        data = event_data[3:-1]
                        self.on_joinuser(data)

                    elif event == 'sendUserList':
                        self.on_send_userlist(event_data[3])

                    elif event == 'camList':
                        cam_data = event_data[3]
                        self.on_cam_list(cam_data)

                    elif event == 'updateRoomSecurity':
                        self.on_update_room_security(event_data)

                    elif event == 'receivePublicMsg':
                        self.on_receive_public_msg(event_data)

                    elif event == 'typingPM':
                        self.on_typing_pm(event_data)

                    elif event == 'pmReceive':
                        self.on_pm_receive(event_data)

                    elif event == 'removeuser':
                        self.on_removeuser(event_data[3])

                    elif event == 'statusUpdate':
                        self.on_status_update(event_data)

                    elif event == 'connectionOK':
                        self.on_connectin_ok(event_data)

                    elif event == 'ytVideoQueueAdd':
                        self.on_yt_video_queue_add(event_data)

                    elif event == 'ytVideoCurrent':
                        self.on_yt_video_current(event_data)

                    elif event == 'ytVideoQueue':
                        self.on_yt_video_queue(event_data)

                    else:
                        print ('Unknown event: `%s`, event data: %s' % (event, event_data))

    def on_result(self, data):
        """
        Default RTMP event.

        :param data: _result data containing information.
        :type data: object
        """
        if isinstance(data, rtmp.pyamf.ASObject):
            if 'code' in data:
                if data['code'] == rtmp.status.NC_CONNECT_REJECTED:
                    if 'application' in data:

                        # TODO: Implement reject event methods based on reject codes.
                        json_data = json.loads(data['application'])

                        reject_code = json_data['reject']
                        if reject_code == '0002':
                            print ('Closed, This room is closed.')
                        elif reject_code == '0003':
                            print ('Closed, That username is taken.')
                        elif reject_code == '0007':
                            print ('Chat version is out of date, please check the protocol version.')
                        elif reject_code == '0008':
                            print ('Room is password protected.')
                        elif reject_code == '0009':
                            print ('You are already in this room, would you like to disconnect the other session?')
                        elif reject_code == '0010':
                            print ('Busy, Server is busy, try again in a few seconds.')
                        elif reject_code == '0012':
                            print ('No Guests, This room does not allow guests.')
                            self.disconnect()
                        elif reject_code == '0013':
                            print ('Reload the page.')
                        elif reject_code == '0015':
                            print ('Unverified, You must verify your account before connecting.')
                        elif reject_code == '0016':
                            print ('Session Closed, Your other session was closed, you may now join the room.')

                        else:
                            print ('Error joining this room. Code: %s' % reject_code)

            if config.DEBUG_TO_CONSOLE:
                for k in data:
                    if isinstance(data, rtmp.pyamf.MixedArray):
                        for kk in data[k]:
                            print ('%s: %s' % (kk, data[k][kk]))
                    else:
                        print ('%s: %s' % (k, data[k]))
        else:
            if config.DEBUG_TO_CONSOLE:
                print (data)

    def on_join_data(self, data):
        """
        Received when a successful connection has been established to the remote stream.

        NOTE: This event is important, as it contains data
        the client needs to send to join the actual room.

        :param data: The join data as a list.
        :type data: list
        """
        self._msg_key = data[7]  # unique identifier for messages?
        self._room_id = data[13]

        json_data = json.loads(data[6])
        self.client_id = json_data['u']

        self.send_connection_ok()

        if config.DEBUG_TO_CONSOLE:
            for i, v in enumerate(data):
                print ('[%s] - %s' % (i, v))

    def on_joinuser(self, data):
        """
        Received when a user joins the room.

        :param data: Information about the user.
        :type data: list
        """
        # TODO: add user data(json_data) to User object.
        # data[1] = mod level ?
        json_data = json.loads(data[2])
        if json_data['u'] != self.client_id:
            print ('%s:%s Joined the room.' % (data[0], json_data['u']))

    def on_send_userlist(self, data):
        json_data = json.loads(data)
        for user_name in json_data:
            # add this data to the user object
            user_data = json.loads(json_data[user_name])
            print ('%s-> %s' % (user_name, user_data))

    def on_cam_list(self, data):
        # add this data to the user object
        json_data = json.loads(data)
        for k in json_data:
            print (json_data[k])

    def on_update_room_security(self, data):
        # this might be related to the room settings.
        if config.DEBUG_TO_CONSOLE:
            print ('Update room security:')
            for i, v in enumerate(data):
                print ('[%s] - %s' % (i, v))

    def on_receive_public_msg(self, data):
        if len(data) > 5:
            # data[3] = unix time stamp including milliseconds.
            user_name = data[4]
            msg = data[5]
            self.message_handler(user_name, msg)

    def message_handler(self, user_name, msg):
        # or overwrite om_receive_public_msg?
        print ('%s: %s' % (user_name, msg))

    def on_typing_pm(self, data):
        """
        Received when a user is writing a private message to the client.

        :param data: Information about who is writing.
        :type data: list
        """
        # data[4] = ?
        print ('%s is typing a private message.' % data[3])

    def on_pm_receive(self, data):
        """
        Received when a user sends the client a private message.

        :param data: Private message information.
        :type data: list
        """
        # data[5] = receiver
        # data[6] = msg color
        # data[7] = ?
        print ('[PM] %s: %s' % (data[3], data[5]))

    def on_removeuser(self, username):
        """
        Received when a user leaves the room.

        :param username: The username of the user leaving the room.
        :type username: str
        """
        print ('%s left the room.' % username)

    def on_status_update(self, data):
        """
        Received when a user changes their status. E.g /afk or /back.

        :param data:
        :type data:
        """
        print ('Status Update: %s' % data)

    def on_connectin_ok(self, data):
        """
        :param data:
        :type data:
        """
        print ('ConnectionOk: %s' % data)

    def on_yt_video_queue_add(self, data):
        """
        Received when a user adds a track to the playlist.

        :param data: List containing data about the track being added.
        :type data: list
        """
        # video_time = data[6]
        # queue number? = data[7]
        print ('%s added %s (%s) to the video queue.' % (data[3], data[5], data[4]))

    def on_yt_video_current(self, data):
        # offset? = data[5]
        # queue number? = data[6]
        print ('Current video: %s (%s)' % (data[4], data[3]))

    def on_yt_video_queue(self, data):
        # not sure what to make of this.
        json_data = json.loads(data[3])
        print ('ytVideoQueue: %s' % json_data['c'])

    # Message construction.
    def send_connection_ok(self):
        """

        """
        self.connection.call(
            'connectionOK',
            [
                self._room_id,
                self._msg_key,
                self.username,
                u'1116348-1751801027-1858934494-1134291946'  # ?
            ]
        )

    def send_public(self, msg):
        """


        :param msg:
        :type msg:
        """
        self.connection.call(
            'send_public',
            [
                self._room_id,
                self._msg_key,
                self.username,
                msg,
                '0',
                '#dddddd',         # text color.
                '3',               # text sizes (0,1,2 or 3)
                self._msg_counter  # message counter.
            ]
        )

    def send_tp_get_queue(self):
        self.connection.call(
            'tpGetQueue',
            [
                self._room_id,
                self._msg_key,
                self.username
            ]
        )

    def send_tp_get_current(self):
        self.connection.call(
            'tpGetCurrent',
            [
                self._room_id,
                self._msg_key,
                self.username
            ]
        )

    def send_change_topic(self, new_topic):
        # based on the info from the decompiled SWF.
        self.connection.call(
            'change_topic',
            [
                self._room_id,
                self._msg_key,
                self.username,
                new_topic
            ]
        )
