#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.networking.cisco.cli.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.cisco.flows.cisco_load_firmware_flow import CiscoLoadFirmwareFlow
from cloudshell.networking.cisco.runners.cisco_firmware_runner import CiscoFirmwareRunner


class CiscoNXOSFirmwareRunner(CiscoFirmwareRunner):
    RELOAD_TIMEOUT = 500

    def __init__(self, cli, logger, resource_config, api, file_system="bootflash:"):
        """Handle firmware upgrade process

        :param CLI cli: Cli object
        :param qs_logger logger: logger
        :param CloudShellAPISession api: cloudshell api object
        :param GenericNetworkingResource resource_config:
        """

        super(CiscoNXOSFirmwareRunner, self).__init__(cli, logger, resource_config, api)
        self._file_system = file_system

    @property
    def cli_handler(self):
        return CiscoCliHandler(self.cli, self.resource_config, self._logger, self.api)

    @property
    def load_firmware_flow(self):
        return CiscoLoadFirmwareFlow(self.cli_handler, self._logger, default_file_system=self._file_system)
