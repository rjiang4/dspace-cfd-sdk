import logging

from config.data_model import ApplicationConfig
from service.configuration_desk_service import ConfigurationDeskService

logger = logging.getLogger(__name__)

class IoService():
    def __init__(self, configuration_desk_service: ConfigurationDeskService):
        """initialization"""
        
        self.active_app = configuration_desk_service.active_app
        self.io_lib = self.active_app.Components.Item('IOFunctionLib')
        self.mdl_tp = self.active_app.Components.Item("ModelTopology")
        
    def config_bus_channel(self, bus_lib, cluster_name: str):
        """ Config Bus Channel """
        
        logger.debug(f" New CAN channel created for: {cluster_name} ")
        bus_lib.CreateChild(bus_lib.DataObjectTypes.Item(0),f"{cluster_name}_CH")
        
        
    def data_port_connection(self, data_port_list1, data_port_list2):
        """ Connect data port block """
        
        for ecu in data_port_list1:
                if ecu.GetCount() != 0:
                    for signal_io in ecu:
                        for signal_asm in data_port_list2:
                            if signal_io.Name == signal_asm.Name:
                                self.active_app.ConnectObjects(signal_io, signal_asm)
        
        
    def data_port_if_mapping(self, app_config: ApplicationConfig):
        """ Map IO and ASM data port block in CFD """
        
        asm_mdl = app_config.m_proj_config.asm_mdl_name
        io_mdl = app_config.m_proj_config.io_mdl_name
        
        self.mdl_tp.Item(f'{asm_mdl}').Item('Input_Interface').Item('BUS_ASM_In').IsInApplication = False
        self.mdl_tp.Item(f'{asm_mdl}').Item('Output_Interface').Item('ASM_BUS_Out').IsInApplication = False
        self.mdl_tp.Item(f'{io_mdl}').Item('BUS').Item('BUS_ASM_Out').IsInApplication = False
        self.mdl_tp.Item(f'{io_mdl}').Item('BUS').Item('ASM_BUS_In').IsInApplication = False

        bus_asm_in = self.mdl_tp.Item(f'{asm_mdl}').Item('Input_Interface').Item('BUS_ASM_In').Item('BUS')
        asm_bus_out = self.mdl_tp.Item(f'{asm_mdl}').Item('Output_Interface').Item('ASM_BUS_Out').Item('BUS')
        bus_asm_out_can = self.mdl_tp.Item(f'{io_mdl}').Item('BUS').Item('BUS_ASM_Out').Item('CAN')
        bus_asm_out_lin = self.mdl_tp.Item(f'{io_mdl}').Item('BUS').Item('BUS_ASM_Out').Item('LIN')
        asm_bus_in_can = self.mdl_tp.Item(f'{io_mdl}').Item('BUS').Item('ASM_BUS_In').Item('CAN')
        asm_bus_in_lin = self.mdl_tp.Item(f'{io_mdl}').Item('BUS').Item('ASM_BUS_In').Item('LIN')

        self.data_port_connection(asm_bus_in_can, asm_bus_out)
        self.data_port_connection(asm_bus_in_lin, asm_bus_out)
        self.data_port_connection(bus_asm_out_can, bus_asm_in)
        self.data_port_connection(bus_asm_out_lin, bus_asm_in)
        