#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.networking.cisco.runners.cisco_connectivity_runner import CiscoConnectivityRunner
from cloudshell.networking.cisco.cli.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.cisco.flows.cisco_add_vlan_flow import CiscoAddVlanFlow
from cloudshell.networking.cisco.flows.cisco_remove_vlan_flow import CiscoRemoveVlanFlow


class CiscoNXOSConnectivityRunner(CiscoConnectivityRunner):
    def __init__(self, cli, logger, api, resource_config):
        """ Handle add/remove vlan flows

        :param cli:
        :param logger:
        :param api:
        :param resource_config:
        """

        super(CiscoNXOSConnectivityRunner, self).__init__(cli, logger, api, resource_config)

    @property
    def add_vlan_flow(self):
        return CiscoAddVlanFlow(self.cli_handler, self._logger, does_require_single_switchport_cmd=True)
