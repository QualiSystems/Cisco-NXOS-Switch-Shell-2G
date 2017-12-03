#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.networking.cisco.nxos.snmp.cisco_nxos_snmp_handler import CiscoNXOSSnmpHandler

from cloudshell.networking.cisco.runners.cisco_autoload_runner import CiscoAutoloadRunner



class CiscoNXOSAutoloadRunner(CiscoAutoloadRunner):
    @property
    def snmp_handler(self):
        return CiscoNXOSSnmpHandler(self._cli, self.resource_config, self._logger, self._api)
