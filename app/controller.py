import logging
import pywintypes
import importlib
import inspect
from pathlib import Path

from service.app_service import ApplicationService
from config.app_config_loader import app_config_loader

logger = logging.getLogger(__name__)

UNIFIED_COM_MATX_NAME = "GPAsystem_MAIN_SystemExtract"

class Controller():
    def __init__(self, yaml_path: Path):
        self.yaml_path = yaml_path
        self.app_config = app_config_loader(yaml_path=self.yaml_path)
        self.app_service = ApplicationService(app_config=self.app_config)

    def pdu_user_code_config(self):
        package_name = "lib"
        BASE_PATH = Path(__file__).resolve().parent.parent
        LIB_PATH = BASE_PATH / package_name
        LIB_PATH_STR = str(LIB_PATH)
        for py_f in LIB_PATH.glob("*.py"):
            py_f_str = str(py_f)
            if py_f_str != "__init__.py" and py_f_str != "Module_Test.py":
                module_name = f"{LIB_PATH_STR}.{py_f_str[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    funcs = inspect.getmembers(module, inspect.isfunction)
                    for name, func in funcs:
                        try:
                            func(self)
                            print(f"function {name} running successfully")
                        except Exception as e:
                            print(f"Error happened when running function: {name}: {e}")
                except Exception as e:
                    print(f"Failed to import {module_name}: {e}")

    def run(self):
        """ application runner """
        
        logger.info(" Start Matlab Project and Config Data Port Blocks ")
        self.app_service.MatlabService.connet_engine()
        self.app_service.MatlabService.data_port_handler(str(self.yaml_path))
        
        logger.info(" Start BusManager Configuration ")
        vcc_cluster = self.app_config.bus_config.vcc_cluster
        non_vcc_cluster = self.app_config.bus_config.non_vcc_cluster

        try:
            cluster_list = (vcc_cluster + non_vcc_cluster) if non_vcc_cluster != None else vcc_cluster
        except TypeError as te:
            if vcc_cluster is None:
                logger.error(" There is no ECU cluster defined ")
                raise te
            elif non_vcc_cluster is None:
                logger.debug(" There is no third-party cluster defined")
                cluster_list = vcc_cluster

        logger.info(" Import Communication Matrix ")
        try:
            # Add CommunicationMatrix
            cmtx_top_nodes = self.app_service.BusManagerService.com_matx_by_cluster_rel.GetTopNodes()
            if cmtx_top_nodes.Count != 0:
                for cmtx_obj in cmtx_top_nodes:
                    self.app_service.BusManagerService.remove_com_mtx(cmtx_obj)
            self.app_service.BusManagerService.import_com_mtx(self.app_config.db_config.db_path)

            if non_vcc_cluster:
                for clusters in non_vcc_cluster:
                    for cluster in clusters.values():
                        com_matx_path = Path(cluster.get('database'))
                        self.app_service.BusManagerService.import_com_mtx(com_matx_path)
        except pywintypes.com_error as e:
            logger.error(e)
        
        try:
            for cluster_i in cluster_list:
                cluster_name = cluster_i["cluster"]
                ecus = cluster_i["ECU"]
                mode = cluster_i["mode"]
                bus_type = cluster_i["type"]
                bus_configuration_name = cluster_name + "_BUS"
                
                # Config Bus Configuration
                logger.info(f" Config Bus Configuration and Assign CommunicationMatrix : {cluster_name} ")
                if self.app_service.BusManagerService.bus_config_rel.FindByXPath(
                    f'/BusConfiguration[@Name = "{bus_configuration_name}"]').Count == 0:
                    self.app_service.BusManagerService.add_bus_configuration(bus_configuration_name)
                
                # Assign Communication Matrix to Bus Configuration 
                bus_configuration = self.app_service.BusManagerService.bus_config_rel.FindByXPath(
                    f'/BusConfiguration[@Name = "{bus_configuration_name}"]')[0]
                
                if bus_type == "CAN":
                    element_type = "BusSystemCan"
                    com_cluster_type = "BusCanCommunicationCluster"
                elif bus_type == "LIN":
                    element_type = "BusSystemLin"
                    com_cluster_type = "BusLinCommunicationCluster"
                else:
                    raise ValueError(f"Wrong BUS type")
                
                ecu_idx = 0
                for ecu in ecus:
                    rx_ipdu = self.app_service.BusManagerService.com_matx_by_cluster_rel.FindByXPath(
                        f'//{element_type}//{com_cluster_type}[@Name= "{cluster_name}" ]'
                        f'//BusNetworkNode[contains(@Name, "{ecu}")]//BusISignalIPdu[@Direction = "RX"]')
                    
                    bus_config_part_inspection = self.app_service.BusManagerService.bus_config_rel.FindByXPath(
                        f'/BusConfiguration[@Name = "{bus_configuration.Name}"]/BusConfigurationPartInspection')[0]
                    
                    tx_ipdu = self.app_service.BusManagerService.com_matx_by_cluster_rel.FindByXPath(
                        f'//{element_type}//{com_cluster_type}[@Name= "{cluster_name}" ]'
                        f'//BusNetworkNode[contains(@Name, "{ecu}")]//BusISignalIPdu[@Direction = "TX"]')
                    
                    bus_config_part_simulated_ECU = self.app_service.BusManagerService.bus_config_rel.FindByXPath(
                        f'/BusConfiguration[@Name = "{bus_configuration.Name}"]/BusConfigurationPartSimulatedEcus')[0]
                    
                    is_ipdu_assigned = False
                    if rx_ipdu.Count != 0:
                        is_ipdu_assigned = True
                        self.app_service.BusManagerService.assign_com_mtx(rx_ipdu, bus_config_part_inspection)
                    
                    if tx_ipdu.Count != 0:
                        is_ipdu_assigned = True
                        if mode[ecu_idx] == "Simulation":
                            self.app_service.BusManagerService.assign_com_mtx(tx_ipdu, bus_config_part_simulated_ECU)
                        else:
                            self.app_service.BusManagerService.assign_com_mtx(tx_ipdu, bus_config_part_inspection)
                    
                    if not is_ipdu_assigned:
                        logger.warning(f" No Tx and Rx IPDU found for {ecu}")

                    ecu_idx = ecu_idx + 1
            
            # Add new BUS channel if necessary
            bus_lib = self.app_service.IoService.io_lib.Item(0).Item(f'{bus_type}')
            try:
                bus_lib.Item(f"{cluster_name}_CH")
            except pywintypes.com_error as e:
                logger.info(f" Start to Config Bus Channel: {cluster_name}_CH ")
                self.app_service.IoService.config_bus_channel(bus_lib=bus_lib, cluster_name=cluster_name)
            
            # Assign Bus Channels 
            logger.info(" Assign Bus Channels ")
            bus_access_req_names = self.app_service.BusManagerService.bus_config_rel.FindByXPath(
                f'/BusConfiguration [@Name = "{cluster_name}_BUS"]/BusConfigurationPartBusAccessRequests/*/*/*/*/@Bus_access')
            if bus_access_req_names.Count != 0:
                for bus_access_req_name in bus_access_req_names:
                    bus_access_req_name.TrySetValue(f"{cluster_name}_CH")
            
        except ValueError as ve:
            logger.error(f"Wrong BUS type for {cluster_name}: {bus_type}")
        
        except IndexError as ie:
            logger.error(f"No Database found for ECU: {ecu}!")
            raise IndexError(f"No Database found for ECU: {ecu}!")
        
        
        # Unify the communication matrix name
        logger.info(f" Unify the communication matrix name to {UNIFIED_COM_MATX_NAME} ")
        bus_com_matx_names = self.app_service.BusManagerService.bus_config_rel.FindByXPath(
            '//BusCommunicationMatrix')
        for bus_com_matx_name in bus_com_matx_names:
            bus_com_matx_name.Name = UNIFIED_COM_MATX_NAME
            
        # Enable Test Automation
        logger.info(" Enable Test Automation ")
        self.app_service.BusManagerService.enable_ta()
        
        # Add Inspection ISignal Feature
        logger.info(" Add Inspection ISignal Feature ")
        self.app_service.BusManagerService.add_insp_isignal_feature()
        
        # Set Update Bit
        logger.info(" Set Update Bit ")
        self.app_service.BusManagerService.set_ub()
        
        # Set QF
        logger.info(" Set QF ")
        self.app_service.BusManagerService.set_qf()
        
        # Set Initial Values
        logger.info(" Set Initial Values ")
        init_v_list = self.app_config.bus_config.init_value
        if not init_v_list:
            logger.warning(" No initial value available ")
        else:
            for init_v in init_v_list:
                cluster_name = init_v["cluster"]
                for signal_name in init_v:
                    if signal_name == 'cluster':
                        continue
                    signal_value = init_v[signal_name]
                    self.app_service.BusManagerService.set_init_value(
                        cluster=cluster_name, signal_name=signal_name, signal_value=signal_value)    
        
        # Signal Mapping
        logger.info(" Signal Mapping ")
        self.app_service.IoService.mdl_tp.Configure("Analyze", [])
        self.app_service.IoService.data_port_if_mapping(app_config=self.app_config)
        if not self.app_config.bus_config.mapping_list:
            logger.warning('No Mapping list available!')
        else:
            for mapping in self.app_config.bus_config.mapping_list:
                cluster_name = mapping["cluster"]
                ecu = mapping["ECU"]
                ecu_dir = mapping["dir"] 
                signal_type = mapping["type"]       
                for function_port_name in mapping:
                    if function_port_name == "ECU" or function_port_name == "dir" \
                        or function_port_name == "cluster" or function_port_name == "type":
                        continue
                    model_port_name = mapping[function_port_name]
                    self.app_service.BusManagerService.map_signal(
                        cluster_name, ecu, ecu_dir, signal_type, function_port_name, model_port_name)

        # Config PDU User Code
        logger.info(" Config PDU User Code ")
        #self.pdu_user_code_config()
