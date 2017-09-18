from __future__ import unicode_literals
import re
import time
from netmiko.cisco_base_connection import CiscoSSHConnection


class BrocadeFastironBase(CiscoSSHConnection):
    """Brocade FastIron aka ICX support."""
    def session_preparation(self):
        """FastIron requires to be enable mode to disable paging."""
        self._test_channel_read()
        self.set_base_prompt()
        self.enable()
        self.disable_paging(command="skip-page-display")
        # Clear the read buffer
        time.sleep(.3 * self.global_delay_factor)
        self.clear_buffer()

    def enable(self, cmd='enable', pattern=r'(ssword|User Name)', re_flags=re.IGNORECASE):
        """Enter enable mode.

        With RADIUS can prompt for User Name

        SSH@Lab-ICX7250>en
        User Name:service_netmiko
        Password:
        SSH@Lab-ICX7250#
        """
        output = ""
        if not self.check_enable_mode():
            count = 4
            i = 1
            while i < count:
                self.write_channel(self.normalize_cmd(cmd))
                new_data = self.read_until_prompt_or_pattern(pattern=pattern, re_flags=re_flags)
                output += new_data
                if 'User Name' in new_data:
                    self.write_channel(self.normalize_cmd(self.username))
                    new_data = self.read_until_prompt_or_pattern(pattern=pattern, re_flags=re_flags)
                    output += new_data
                if 'ssword' in new_data:
                    self.write_channel(self.normalize_cmd(self.secret))
                    output += self.read_until_prompt()
                    return output
                time.sleep(1)
                i += 1

        if not self.check_enable_mode():
            msg = "Failed to enter enable mode. Please ensure you pass " \
                  "the 'secret' argument to ConnectHandler."
            raise ValueError(msg)


class BrocadeFastironTelnet(BrocadeFastironBase):
    def __init__(self, *args, **kwargs):
        super(BrocadeFastironTelnet, self).__init__(*args, **kwargs)
        self.RETURN = '\r\n'

    def telnet_login(self, pri_prompt_terminator='#', alt_prompt_terminator='>',
                     username_pattern=r"Username:", pwd_pattern=r"assword:",
                     delay_factor=1, max_loops=60):
        """Telnet login. Can be username/password or just password."""
        super(BrocadeFastironTelnet, self).telnet_login(
                pri_prompt_terminator=pri_prompt_terminator,
                alt_prompt_terminator=alt_prompt_terminator,
                username_pattern=username_pattern,
                pwd_pattern=pwd_pattern,
                delay_factor=delay_factor,
                max_loops=max_loops)


class BrocadeFastironSSH(BrocadeFastironBase):
    pass