import logging
import matlab.engine

from pathlib import Path

from config.data_model import ApplicationConfig

logger = logging.getLogger(__name__)

class MatlabService():
    def __init__(self, app_config: ApplicationConfig):
        """ initialization """
        
        self.app_config = app_config
        self.m_eng = None
        
        self._m_prj_path = self.app_config.m_proj_config.m_proj_path

        # Data port block names
        self._ext_in = None
        self._ext_out = None
        self._bus_sim = None
        self._bus_ins = None
        self.dp_block = []
        self.dp_name = ["External_In", "External_Out", "Bus_Simulation", "Bus_Inspection"]
            
    def connect_engine(self):
        """ Connect Matlab engine """
        
        if not matlab.engine.find_matlab():
            logger.debug('Starting Matlab')
            self.m_eng = matlab.engine.start_matlab("-desktop")
        else:
            logger.debug('Connecting Matlab')
            self.m_eng = matlab.engine.connect_matlab('MATLABEngine')
            
    def data_port_handler(self, yaml_path: Path):
        self.m_eng.addpath(self.app_config.m_proj_config.m_script_path)
        if self.app_config.cfd_config.cfd_app_name == "SysInt":
            self.m_eng.workspace['BCMx_Variant'] = 0
        else:
            self.m_eng.workspace['BCMx_Variant'] = 1
        self.m_eng.DataPortUpdater(yaml_path, self.app_config.m_proj_config.m_proj_path, nargout=0)
        

    def data_port_updater(self):
        self.m_eng.openProject(self._m_prj_path, nargout = 0)
        self.m_eng.find_system()

