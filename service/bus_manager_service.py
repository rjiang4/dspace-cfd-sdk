import logging
import pywintypes
from pathlib import Path
from service.configuration_desk_service import ConfigurationDeskService
from config.data_model import ApplicationConfig

logger = logging.getLogger(__name__)

class BusManagerService():
    def __init__(self, configuration_desk_service: ConfigurationDeskService):
        """Initialization"""
        
        self.active_app = configuration_desk_service.active_app
        self.bus_mgr = self.active_app.Components.Item("BusManager")
        self.bus_config_rel = self.active_app.Relations.Item("BusConfigurations")
        self.bus_config_types = self.bus_config_rel.GetCreatableTypes().Item(0)
        self.com_matx_by_cluster_rel = self.active_app.Relations.Item("CommunicationMatricesByClusters")
        self.bus_model_if = self.active_app.Components.Item('ModelTopology').Item(f'IO').Item('BUS')
        self.can_model_if = self.active_app.Components.Item('ModelTopology').Item(f'IO').Item('BUS').Item('CAN')
        
    def import_com_mtx(self, db_path: str):
        """
        Add communication matrix
        
        db_path:
            Path to the database root folder
        """

        db_path = Path(db_path)
        
        for item in db_path.rglob("*"):
            if item.is_file():
                logger.info("Adding ComMatx: " + str(item.resolve()))
                try:
                    self.bus_mgr.Configure('AddCommunicationMatrix', [str(item.resolve())])
                except pywintypes.com_error as e:
                    logger.warning(f"CommunicationMatrix already exist!")    
                    
    def remove_com_mtx(self, com_mtx):
        """
        Remove all communication matrix 
        """
        
        logger.debug("Removing communication matrix: " + com_mtx.Name)
        
        self.bus_mgr.Configure('RemoveCommunicationMatrix', [com_mtx, 'True'])
                    
    def add_bus_configuration(self, bus_configuration_name: str):
        """
        Add Bus configuration
        """
        
        logger.debug("Create bus configuration: " + bus_configuration_name)
        
        #Create new Bus configuration
        bus_configuration = self.bus_config_rel.CreateDataObject(self.bus_config_types)
        bus_configuration.Name = bus_configuration_name
        
        #Make variable description path to complete
        variable_description = bus_configuration.Properties.Item('Variable description')
        variable_description.TrySetValue('Complete')
        
        #Assign application process
        application_process = bus_configuration.Properties.Item('ManuallyAssignedApplicationProcess')

    def assign_com_mtx(self, bus_network_node, bus_configuration):
        """
        Assign signals from communication matrix to Bus configuration
        """
        
        self.bus_mgr.Configure('AssignElements', [bus_network_node, bus_configuration])
    
    def unassign_com_mtx(self, bus_configuration_name: str):
        """ Unassign communication matrix for Bus configuration """
        
        logger.debug("unassign communication matrix for: " + bus_configuration_name)
        
        bus_configuration = self.bus_config_rel.GetTopNodes().Item(bus_configuration_name)
        sim_ecus = self.bus_config_rel.GetElements(bus_configuration).Item("Simulated ECUs")
        
        for com_mtx in self.bus_config_rel.GetElements(sim_ecus):
            self.bus_mgr.Configure("RemoveElements", [com_mtx])
            
    def add_insp_isignal_feature(self):
        """ Add isignal feature for inspection signals """
        
        bus_isignal_insp = self.bus_config_rel.FindByXPath('//BusConfigurationPartInspection//BusISignal')
        
        self.bus_mgr.Configure('AddFeature', ['BusISignalValueInspection', bus_isignal_insp])
        
    def enable_ta(self):
        """ Enable test automation for all isignals """
        
        #Lock the gui to speed up
        wt = self.active_app.TransactionCreator.CreateWriteTransaction("BusManager")
        
        ta_supports = self.bus_config_rel.FindByXPath(
            '//BusConfigurationPartSimulatedEcus//FunctionPort/@IsTestAutomationSupportEnabled')

        for ta_support in ta_supports:
            ta_support.TrySetValue(True)
            
        wt.Close()
        
    def set_ub(self):
        """ Set update bit to true """
        
        init_sw_settings = self.bus_config_rel.FindByXPath(
            '//BusConfigurationPartSimulatedEcus//FunctionPort[contains(@Name, "UpdateBit Value")]'
            f'/@InitialSwitchSetting')
        
        init_values = self.bus_config_rel.FindByXPath(
            '//BusConfigurationPartSimulatedEcus//FunctionPort[contains(@Name, "UpdateBit Value")]'
            f'/@InitialSubstituteValue')
        
        for init_sw_setting in init_sw_settings:
            init_sw_setting.TrySetValue("Substitute value")
        for init_value in init_values:
            init_value.TrySetValue(1)
        
    def set_qf(self):
        """ Set qf values to high """
        
        qf_list = ["Qf Value", "QF Value", "Qly"]
        
        for qf in qf_list:
            init_sw_settings = self.bus_config_rel.FindByXPath(
                f'//BusConfigurationPartSimulatedEcus//FunctionPort[contains(@Name, "{qf}")]'
                f'/@InitialSwitchSetting')
            
            init_values = self.bus_config_rel.FindByXPath(
                f'//BusConfigurationPartSimulatedEcus//FunctionPort[contains(@Name, "{qf}")]'
                f'/@InitialSubstituteValue')
            
            for init_sw_setting in init_sw_settings:
                init_sw_setting.TrySetValue("Substitute value")
            for init_value in init_values:
                init_value.TrySetValue(3)
                
        #Special case for signal isHvSysRQlyFac
        init_sw_setting = self.bus_config_rel.FindByXPath(
            f'//BusConfigurationPartSimulatedEcus//FunctionPort[@Name = "isHvSysRQlyFac Value"]'
            f'/@InitialSwitchSetting')[0]
        init_sw_setting.TrySetValue("Model signal")
        
    def set_init_value(self, cluster, signal_name, signal_value):
        """ 
        Set initial value for isignals
        
        cluster:
            Bus cluster
        
        signal_name -> str:
            Signal name
        
        signal_value -> str:
            Signal value
        """
        
        wt = self.active_app.TransactionCreator.CreateWriteTransaction("BusManager")
        
        init_sw_setting = self.bus_config_rel.FindByXPath(
            f'//BusConfiguration[@Name = "{cluster}_BUS"]//BusConfigurationPartSimulatedEcus'
            f'//FunctionPort[contains(@Name, "{signal_name} Value")]/@InitialSwitchSetting')
        
        init_value = self.bus_config_rel.FindByXPath(
            f'//BusConfiguration[@Name = "{cluster}_BUS"]//BusConfigurationPartSimulatedEcus'
            f'//FunctionPort[contains(@Name, "{signal_name} Value")]/@InitialSubstituteValue')
        
        try:
            init_sw_setting.Item(0).TrySetValue("Substitute value")
            init_value.Item(0).TrySetValue(signal_value)
            
            logger.debug(f"Setting Setting Initial Value: {cluster} : {signal_name} to {signal_value}")
            
        except pywintypes.com_error:
            logger.warning(f"{signal_name} in {cluster}_BUS cannot be found! ")
            
        wt.Close()
        
    def map_signal(self, cluster, ecu, ecu_dir, signal_type, function_port, model_port):
        """
        Map signal in BusManager
        
        cluster -> str:
            Bus cluster name
            
        ecu -> str:
            ECU name
        
        ecu_dir -> str:
            ECU direction [Sim/Ins]
            
        signal_type -> str:
            Signal type [CAN/LIN]
            
        function_port:
            ISignal function port in BusConfiguration
            
        model_port:
            Model port in ConfigurationDesk
        """
        
        bus_config = cluster + "_BUS"
        try:
            if ecu_dir == "Sim":
                    function_port = self.bus_config_rel.FindByXPath(
                        f'/BusConfiguration[@Name = "{bus_config}"]//BusConfigurationPartSimulatedEcus'
                        f'//FunctionPort[@Name = "{function_port}"]')[0]
            else:
                    function_port = self.bus_config_rel.FindByXPath(
                        f'/BusConfiguration[@Name = "{bus_config}"]//BusConfigurationPartInspection'
                        f'//FunctionPort[@Name = "{function_port}"]')[0]
                    
        except IndexError:
            logger.warning(f"In {cluster}, {function_port} is not exist!")
            
        # Enable model access
        mapping_support = function_port.Properties.Item('IsMappable')
        mapping_support.TrySetValue(True)
        
        # Get signal port
        block_name = ecu_dir + "_" + signal_type
        model_port = self.bus_model_if.Item(f'{signal_type}').Item(block_name).Item(f"{signal_type}").Item(ecu).Item(model_port)
        self.active_app.ConnectObjects(function_port, model_port)
        