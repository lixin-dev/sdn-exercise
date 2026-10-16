# SPDX-FileCopyrightText: 2013 Barefoot Networks, Inc.
#
# SPDX-License-Identifier: Apache-2.0

import os
import socket
import tempfile
from sys import exit
from time import sleep

from mininet.log import debug, error, info
from mininet.moduledeps import pathCheck
from mininet.node import Host, Switch


class P4Host(Host):
    def config(self, **params):
        r = super(P4Host, self).config(**params)

        for off in ["rx", "tx", "sg"]:
            cmd = "/sbin/ethtool --offload %s %s off" % (self.defaultIntf().name, off)
            self.cmd(cmd)

        # disable IPv6
        self.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        self.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        self.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

        return r

    def describe(self, sw_addr=None, sw_mac=None):
        print("**********")
        print("Network configuration for: %s" % self.name)
        print("Default interface: %s\t%s\t%s" % (
            self.defaultIntf().name,
            self.defaultIntf().IP(),
            self.defaultIntf().MAC()
        ))
        if sw_addr is not None or sw_mac is not None:
            print("Default route to switch: %s (%s)" % (sw_addr, sw_mac))
        print("**********")

