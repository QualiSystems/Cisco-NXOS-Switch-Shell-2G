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
from cloudshell.networking.cisco.snmp.cisco_snmp_handler import CiscoSnmpHandler, \
    CiscoEnableDisableSnmpFlow
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
        api = CloudShellSessionContext(context).get_api()
        resource_config = NetworkingResourceConfig.from_context(
            context=context, api=api
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
                context=context,
                api=api,
            )
            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            enable_disable_flow = CiscoEnableDisableSnmpFlow(cli_handler, logger)
            snmp_handler = CiscoSnmpHandler.from_config(
                enable_disable_flow, resource_config, logger
            )
            autoload_operations = CiscoSnmpAutoloadFlow(
                logger=logger, snmp_handler=snmp_handler
            )

            resource_model = NetworkingResourceModel.from_resource_config(
                resource_config
            )

            response = autoload_operations.discover(
                self.SUPPORTED_OS, resource_model
            )
            logger.info("'Autoload' command completed")

            return response
    def run_custom_command(
        self, context: ResourceCommandContext, custom_command: str
    ) -> str:
        """Send custom command.

        :param custom_command: Command user wants to send to the device.
        :param context: an object with all Resource Attributes inside
        :return: result
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
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

            return response

    def run_custom_config_command(
        self, context: ResourceCommandContext, custom_command: str
    ) -> str:
        """Send custom command in configuration mode.

        :param custom_command: Command user wants to send to the device
        :param context: an object with all Resource Attributes inside
        :return: result
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                context=context,
                api=api,
            )

            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            send_command_operations = CiscoRunCommandFlow(
                logger=logger, cli_configurator=cli_handler
            )

            result_str = send_command_operations.run_custom_config_command(
                custom_command=custom_command
            )

            return result_str

    def ApplyConnectivityChanges(
        self, context: ResourceCommandContext, request: str
    ) -> str:
        """
        Create vlan and add or remove it to/from network interface.

        :param context: an object with all Resource Attributes inside
        :param str request: request json
        :return:
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                context=context,
                api=api,
            )

            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            connectivity_operations = CiscoNXOSConnectivityFlow(
                logger=logger,
                cli_handler=cli_handler,
                support_multi_vlan_str=True,
                support_vlan_range_str=True,
                is_switch=True,
            )
            logger.info("Start applying connectivity changes.")
            result = connectivity_operations.apply_connectivity(request=request)
            logger.info("Apply Connectivity changes completed")
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
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                context=context,
                api=api,
            )

            if not configuration_type:
                configuration_type = "running"

            if not vrf_management_name:
                vrf_management_name = resource_config.vrf_management_name

            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            configuration_flow = CiscoNXOSConfigurationFlow(
                cli_handler=cli_handler, logger=logger, resource_config=resource_config
            )

            logger.info("Save started")
            response = configuration_flow.save(
                folder_path=folder_path,
                configuration_type=configuration_type,
                vrf_management_name=vrf_management_name,
            )
            logger.info("Save completed")
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
        """Restore selected file to the provided destination.

        :param context: an object with all Resource Attributes inside
        :param path: source config file
        :param configuration_type: running or startup configs
        :param restore_method: append or override methods
        :param vrf_management_name: VRF management Name
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                context=context,
                api=api,
            )

            if not configuration_type:
                configuration_type = "running"

            if not restore_method:
                restore_method = "override"

            if not vrf_management_name:
                vrf_management_name = resource_config.vrf_management_name

            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            configuration_flow = CiscoNXOSConfigurationFlow(
                cli_handler=cli_handler, logger=logger, resource_config=resource_config
            )

            logger.info("Restore started")
            configuration_flow.restore(
                path=path,
                restore_method=restore_method,
                configuration_type=configuration_type,
                vrf_management_name=vrf_management_name,
            )
            logger.info("Restore completed")


    def orchestration_save(
        self, context: ResourceCommandContext, mode: str, custom_params: str
    ) -> str:
        """Save selected file to the provided destination.

        :param context: an object with all Resource Attributes inside
        :param mode: mode
        :param custom_params: json with custom save parameters
        :return str response: response json
        """
        if not mode:
            mode = "shallow"

        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                context=context,
                api=api,
            )

            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            configuration_flow = CiscoNXOSConfigurationFlow(
                cli_handler=cli_handler, logger=logger, resource_config=resource_config
            )

            logger.info("Orchestration save started")
            response = configuration_flow.orchestration_save(
                mode=mode, custom_params=custom_params
            )
            response_json = OrchestrationSaveRestore(
                logger, resource_config.name
            ).prepare_orchestration_save_result(response)
            logger.info("Orchestration save completed")
            return response_json

    def orchestration_restore(
        self,
        context: ResourceCommandContext,
        saved_artifact_info: str,
        custom_params: str,
    ):
        """Restore selected file to the provided destination.

        :param context: an object with all Resource Attributes inside
        :param saved_artifact_info: OrchestrationSavedArtifactInfo json
        :param custom_params: json with custom restore parameters
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                context=context,
                api=api,
            )

            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            configuration_flow = CiscoNXOSConfigurationFlow(
                cli_handler=cli_handler, logger=logger, resource_config=resource_config
            )

            logger.info("Orchestration restore started")
            restore_params = OrchestrationSaveRestore(
                resource_config.name
            ).parse_orchestration_save_result(saved_artifact_info)
            configuration_flow.restore(**restore_params)
            logger.info("Orchestration restore completed")

    @GlobalLock.lock
    def load_firmware(
        self, context: ResourceCommandContext, path: str, vrf_management_name: str
    ):
        """Upload and updates firmware on the resource."""
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                context=context,
                api=api,
            )

            if not vrf_management_name:
                vrf_management_name = resource_config.vrf_management_name

            cli_handler = self._cli.get_cli_handler(resource_config, logger)

            logger.info("Start Load Firmware")
            firmware_operations = CiscoLoadFirmwareFlow(
                cli_handler=cli_handler, logger=logger
            )
            firmware_operations.load_firmware(
                path=path, vrf_management_name=vrf_management_name
            )
            logger.info("Finish Load Firmware.")

    def health_check(self, context: ResourceCommandContext):
        """Performs device health check.

        :param context: an object with all Resource Attributes inside
        :return: Success or Error message
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
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
            return state_operations.health_check()

    def cleanup(self):
        pass

    def shutdown(self, context: ResourceCommandContext):
        """Shutdown device.

        :param context: an object with all Resource Attributes inside
        :return:
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
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

            return state_operations.shutdown()
