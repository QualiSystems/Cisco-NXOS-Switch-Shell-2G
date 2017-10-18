#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.networking.cisco.nxos.flows.cisco_nxos_add_vlan_flow import CiscoNXOSAddVlanFlow
from cloudshell.networking.cisco.nxos.flows.cisco_nxos_remove_vlan_flow import CiscoNXOSRemoveVlanFlow
from cloudshell.networking.cisco.runners.cisco_connectivity_runner import CiscoConnectivityRunner
from cloudshell.networking.cisco.cli.cisco_cli_handler import CiscoCliHandler



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
    def cli_handler(self):
        return CiscoCliHandler(self.cli, self.resource_config, self._logger, self.api)

    @property
    def add_vlan_flow(self):
        return CiscoNXOSAddVlanFlow(self.cli_handler, self._logger)

    @property
    def remove_vlan_flow(self):
        return CiscoNXOSRemoveVlanFlow(self.cli_handler, self._logger)
