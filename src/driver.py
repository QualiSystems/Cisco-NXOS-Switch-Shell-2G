from cloudshell.networking.cisco.flows.cisco_autoload_flow import CiscoSnmpAutoloadFlow
from cloudshell.networking.cisco.flows.cisco_load_firmware_flow import (
    CiscoLoadFirmwareFlow,
)
from cloudshell.networking.cisco.flows.cisco_run_command_flow import CiscoRunCommandFlow
from cloudshell.networking.cisco.flows.cisco_state_flow import CiscoStateFlow
from cloudshell.networking.cisco.nxos.cli.cisco_nxos_cli_handler import CiscoNXOSCli
from cloudshell.networking.cisco.nxos.flows.cisco_nxos_configuration_flow import (
    CiscoNXOSConfigurationFlow,
)
from cloudshell.networking.cisco.nxos.flows.cisco_nxos_connectivity_flow import (
    CiscoNXOSConnectivityFlow,
)
from cloudshell.networking.cisco.snmp.cisco_snmp_handler import CiscoSnmpHandler
from cloudshell.shell.core.driver_context import (
    AutoLoadCommandContext,
    AutoLoadDetails,
    InitCommandContext,
    ResourceCommandContext,
)
from cloudshell.shell.core.driver_utils import GlobalLock
from cloudshell.shell.core.orchestration_save_restore import OrchestrationSaveRestore
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from cloudshell.shell.standards.networking.autoload_model import NetworkingResourceModel
from cloudshell.shell.standards.networking.driver_interface import (
    NetworkingResourceDriverInterface,
)
from cloudshell.shell.standards.networking.resource_config import (
    NetworkingResourceConfig,
)


class CiscoNXOSShellDriver(
    ResourceDriverInterface, NetworkingResourceDriverInterface, GlobalLock
):
    SUPPORTED_OS = ["NX[ -]?OS|NXOS"]
    SHELL_NAME = "Cisco NXOS Switch 2G"

    def __init__(self):
        super(CiscoNXOSShellDriver, self).__init__()
        self._cli = None

    def initialize(self, context: InitCommandContext):
        resource_config = NetworkingResourceConfig.from_context(
            shell_name=self.SHELL_NAME, supported_os=self.SUPPORTED_OS, context=context
        )

        self._cli = CiscoNXOSCli(resource_config)
        return "Finished initializing"

    @GlobalLock.lock
    def get_inventory(self, context: AutoLoadCommandContext) -> AutoLoadDetails:
        """Return device structure with all standard attributes."""
        with LoggingSessionContext(context) as logger:
            logger.info("Starting 'Autoload' command ...")
            api = CloudShellSessionContext(context).get_api()
            resource_config = NetworkingResourceConfig.from_context(
                shell_name=self.SHELL_NAME,
                supported_os=self.SUPPORTED_OS,
                context=context,
                api=api,
            )
            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            snmp_handler = CiscoSnmpHandler(resource_config, logger, cli_handler)
            autoload_operations = CiscoSnmpAutoloadFlow(
                logger=logger, snmp_handler=snmp_handler
            )

            resource_model = NetworkingResourceModel(
                resource_config.name,
                resource_config.shell_name,
                resource_config.family_name,
            )

            response = autoload_operations.discover(
                resource_config.supported_os, resource_model
            )
            logger.info("'Autoload' command completed")

            return response

    def run_custom_command(
        self, context: ResourceCommandContext, custom_command: str
    ) -> str:
        """Send custom command."""
        with LoggingSessionContext(context) as logger:
            logger.info("Starting 'Run Custom Command' command ...")
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                shell_name=self.SHELL_NAME,
                supported_os=self.SUPPORTED_OS,
                context=context,
                api=api,
            )

            cli_handler = self._cli.get_cli_handler(resource_config, logger)

            send_command_operations = CiscoRunCommandFlow(
                logger=logger, cli_configurator=cli_handler
            )

            response = send_command_operations.run_custom_command(
                custom_command=custom_command
            )

            logger.info("'Run Custom Command' command completed")
            return response

    def run_custom_config_command(
        self, context: ResourceCommandContext, custom_command: str
    ) -> str:
        """Send custom command in configuration mode."""
        with LoggingSessionContext(context) as logger:
            logger.info("Starting 'Run Custom Config Command' command ...")
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                shell_name=self.SHELL_NAME,
                supported_os=self.SUPPORTED_OS,
                context=context,
                api=api,
            )

            cli_handler = self._cli.get_cli_handler(resource_config, logger)

            send_command_operations = CiscoRunCommandFlow(
                logger=logger, cli_configurator=cli_handler
            )
            response = send_command_operations.run_custom_config_command(
                custom_command=custom_command
            )

            logger.info("'Run Custom Config Command' command completed")
            return response

    def ApplyConnectivityChanges(
        self, context: ResourceCommandContext, request: str
    ) -> str:
        """Create VLAN and add/remove it to/from network interface."""
        with LoggingSessionContext(context) as logger:
            logger.info("Starting 'Apply Connectivity Changes' command ...")
            logger.info(f"Request: {request}")

            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                shell_name=self.SHELL_NAME,
                supported_os=self.SUPPORTED_OS,
                context=context,
                api=api,
            )

            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            connectivity_operations = CiscoNXOSConnectivityFlow(
                logger=logger, cli_handler=cli_handler
            )
            result = connectivity_operations.apply_connectivity_changes(request=request)

            logger.info(
                f"'Apply Connectivity Changes' command completed with result '{result}'"
            )
            return result

    def save(
        self,
        context: ResourceCommandContext,
        folder_path: str,
        configuration_type: str,
        vrf_management_name: str,
    ) -> str:
        """Save selected file to the provided destination."""
        with LoggingSessionContext(context) as logger:
            logger.info("Starting 'Save' command ...")
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                shell_name=self.SHELL_NAME,
                supported_os=self.SUPPORTED_OS,
                context=context,
                api=api,
            )

            configuration_type = configuration_type or "running"
            vrf_management_name = (
                vrf_management_name or resource_config.vrf_management_name
            )

            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            configuration_flow = CiscoNXOSConfigurationFlow(
                cli_handler=cli_handler, logger=logger, resource_config=resource_config
            )

            response = configuration_flow.save(
                folder_path=folder_path,
                configuration_type=configuration_type,
                vrf_management_name=vrf_management_name,
            )

            logger.info("'Save' command completed")
            return response

    @GlobalLock.lock
    def restore(
        self,
        context: ResourceCommandContext,
        path: str,
        configuration_type: str,
        restore_method: str,
        vrf_management_name: str,
    ):
        """Restore selected file to the provided destination."""
        with LoggingSessionContext(context) as logger:
            logger.info("Starting 'Restore' command ...")
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                shell_name=self.SHELL_NAME,
                supported_os=self.SUPPORTED_OS,
                context=context,
                api=api,
            )

            configuration_type = configuration_type or "running"
            restore_method = restore_method or "override"
            vrf_management_name = (
                vrf_management_name or resource_config.vrf_management_name
            )

            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            configuration_flow = CiscoNXOSConfigurationFlow(
                cli_handler=cli_handler, logger=logger, resource_config=resource_config
            )

            configuration_flow.restore(
                path=path,
                restore_method=restore_method,
                configuration_type=configuration_type,
                vrf_management_name=vrf_management_name,
            )

            logger.info("'Restore' command completed")

    def orchestration_save(
        self, context: ResourceCommandContext, mode: str, custom_params: str
    ) -> str:
        with LoggingSessionContext(context) as logger:
            logger.info("Starting 'Orchestration Save' command ...")
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                shell_name=self.SHELL_NAME,
                supported_os=self.SUPPORTED_OS,
                context=context,
                api=api,
            )

            mode = mode or "shallow"

            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            configuration_flow = CiscoNXOSConfigurationFlow(
                cli_handler=cli_handler, logger=logger, resource_config=resource_config
            )

            response = configuration_flow.orchestration_save(
                mode=mode, custom_params=custom_params
            )

            response_json = OrchestrationSaveRestore(
                logger, resource_config.name
            ).prepare_orchestration_save_result(response)

            logger.info("'Orchestration Save' command completed")
            return response_json

    def orchestration_restore(
        self,
        context: ResourceCommandContext,
        saved_artifact_info: str,
        custom_params: str,
    ):
        with LoggingSessionContext(context) as logger:
            logger.info("Starting 'Orchestration Restore' command ...")
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                shell_name=self.SHELL_NAME,
                supported_os=self.SUPPORTED_OS,
                context=context,
                api=api,
            )

            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            configuration_flow = CiscoNXOSConfigurationFlow(
                cli_handler=cli_handler, logger=logger, resource_config=resource_config
            )

            restore_params = OrchestrationSaveRestore(
                logger, resource_config.name
            ).parse_orchestration_save_result(saved_artifact_info)

            configuration_flow.restore(**restore_params)
            logger.info("'Orchestration Restore' command completed")

    @GlobalLock.lock
    def load_firmware(
        self, context: ResourceCommandContext, path: str, vrf_management_name: str
    ):
        """Upload and updates firmware on the resource."""
        with LoggingSessionContext(context) as logger:
            logger.info("Starting 'Load Firmware' command ...")
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                shell_name=self.SHELL_NAME,
                supported_os=self.SUPPORTED_OS,
                context=context,
                api=api,
            )

            vrf_management_name = (
                vrf_management_name or resource_config.vrf_management_name
            )
            cli_handler = self._cli.get_cli_handler(resource_config, logger)

            firmware_operations = CiscoLoadFirmwareFlow(
                cli_handler=cli_handler, logger=logger
            )
            firmware_operations.load_firmware(
                path=path, vrf_management_name=vrf_management_name
            )
            logger.info("'Load Firmware' command completed")

    def health_check(self, context: ResourceCommandContext) -> str:
        """Performs device health check."""
        with LoggingSessionContext(context) as logger:
            logger.info("Starting 'Health Check' command ...")

            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                shell_name=self.SHELL_NAME,
                supported_os=self.SUPPORTED_OS,
                context=context,
                api=api,
            )

            cli_handler = self._cli.get_cli_handler(resource_config, logger)

            state_operations = CiscoStateFlow(
                logger=logger,
                api=api,
                resource_config=resource_config,
                cli_configurator=cli_handler,
            )

            result = state_operations.health_check()
            logger.info(f"'Health Check' command completed with result '{result}'")

            return result

    def cleanup(self):
        pass

    def shutdown(self, context: ResourceCommandContext):
        """Shutdown device."""
        with LoggingSessionContext(context) as logger:
            logger.info("Starting 'Shutdown' command ...")
            api = CloudShellSessionContext(context).get_api()
            resource_config = NetworkingResourceConfig.from_context(
                shell_name=self.SHELL_NAME,
                supported_os=self.SUPPORTED_OS,
                context=context,
                api=api,
            )

            cli_handler = self._cli.get_cli_handler(resource_config, logger)

            state_operations = CiscoStateFlow(
                logger=logger,
                api=api,
                resource_config=resource_config,
                cli_configurator=cli_handler,
            )

            state_operations.shutdown()
            logger.info("'Shutdown' command completed")
