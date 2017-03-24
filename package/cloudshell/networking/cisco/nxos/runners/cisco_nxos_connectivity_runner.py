#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.networking.cisco.runners.cisco_connectivity_runner import CiscoConnectivityRunner
from cloudshell.networking.cisco.flows.cisco_add_vlan_flow import CiscoAddVlanFlow


class CiscoNXOSConnectivityRunner(CiscoConnectivityRunner):
    @property
    def add_vlan_flow(self):
        return CiscoAddVlanFlow(self.cli_handler, self._logger, does_require_single_switchport_cmd=True)
