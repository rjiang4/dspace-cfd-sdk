import logging
import matlab.engine

from pathlib import Path

from config.data_model import ApplicationConfig

logger = logging.getLogger(__name__)

class MatlabService():
    def __init__(self, app_config: ApplicationConfig):
        """ initialization """
        
        self.app_config = app_config
        self.Matlab_Eng = None
            
    def connet_engine(self):
        """ Connect Matlab engine """
        
        if not matlab.engine.find_matlab():
            logger.debug('Starting Matlab')
            self.Matlab_Eng = matlab.engine.start_matlab("-desktop")
        else:
            logger.debug('Connecting Matlab')
            self.Matlab_Eng = matlab.engine.connect_matlab('MATLABEngine')
            
    def data_port_handler(self, yaml_path: Path):
        self.Matlab_Eng.addpath(self.app_config.m_proj_config.m_script_path)
        if self.app_config.cfd_config.cfd_app_name == "SysInt":
            self.Matlab_Eng.workspace['BCMx_Variant'] = 0
        else:
            self.Matlab_Eng.workspace['BCMx_Variant'] = 1
        self.Matlab_Eng.DataPortUpdater(yaml_path, self.app_config.m_proj_config.m_proj_path, nargout=0)
        