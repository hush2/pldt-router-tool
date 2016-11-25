#
# PLDT Router Tool
# https://github.com/hush2
#
# Tested on PLDT Baudtec RNR4_A72T_PLD_0.19
#

import socket
import telnetlib


class TelnetClientException(Exception):
    pass


class TelnetClient:
    CR = b'\r'  # carriage return
    CRLF = b'\r\n'  # line feed
    TELNET_PROMPT = CRLF + b'$'
    DEFAULT_TIMEOUT = 2

    # router telnet commands
    SHOW_STATUS = b'show status'
    SHOW_ADSL_ADSL = b'show wan adsl'
    SHOW_WLAN_CLIENT = b'show wlan client'
    SHOW_WLAN_BASIC = b'show wlan basic'
    REBOOT = b'reboot'

    telnet = False

    def __init__(self, ip, port=23):
        try:
            self.telnet = telnetlib.Telnet(ip, port, self.DEFAULT_TIMEOUT)
        except socket.timeout as e:
            raise TelnetClientException("Can't connect to {0}:{1}".format(ip, port))

    def login(self, username, password):
        """ Login to router. Strings should be converted to bytes. """

        if not self.telnet:
            raise TelnetClientException('Telnet not connected.')

        result = self.telnet.expect([b'\\r\\nUsername:\s'], 2)
        if result[0] < 0:
            raise TelnetClientException('Username prompt not found.')

        self.telnet.write(str.encode(username) + self.CR)
        self.telnet.read_until(b'Password: ')

        self.telnet.write(str.encode(password) + self.CR)

        result = self.telnet.read_until(self.TELNET_PROMPT, self.DEFAULT_TIMEOUT)

        if "Bad username/Password" in str(result):
            raise TelnetClientException('Wrong User/Pass.')

        # In case read timeout, verify if prompt received
        elif not result[-3:] == self.TELNET_PROMPT:
            raise TelnetClientException('Telnet prompt not found.')

    def send_command(self, command):
        """ Send commands to router. Strings should be converted to bytes. """

        self.telnet.write(command + self.CR)
        text = self.telnet.read_until(self.TELNET_PROMPT)
        return text.decode()

    def close(self):
        self.telnet.close()


if __name__ == '__main__':
    tc = TelnetClient('192.168.1.1')
    tc.login('admin', '1234')
    status = tc.send_command(TelnetClient.SHOW_STATUS)
    print(status)
