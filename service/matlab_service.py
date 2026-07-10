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
        
        self._m_prj_config = self.app_config.m_proj_config
        self._mapping_list = self.app_config.bus_config.mapping_list
        
        # Data port block names
        self._ext_in = None
        self._ext_out = None
        self._bus_sim = None
        self._bus_ins = None
        self._dp_block = {}
        self._dp_name = ["External_In", "External_Out", "Bus_Simulation", "Bus_Inspection"]
            
    def connect_engine(self):
        """ Connect Matlab engine """
        
        if not matlab.engine.find_matlab():
            logger.debug('Starting Matlab')
            self.m_eng = matlab.engine.start_matlab("-desktop")
        else:
            logger.debug('Connecting Matlab')
            self.m_eng = matlab.engine.connect_matlab('MATLABEngine')
            
    def data_port_handler(self, yaml_path: Path):
        if self.app_config.cfd_config.cfd_app_name == "SysInt":
            self.m_eng.workspace['BCMx_Variant'] = 0
        else:
            self.m_eng.workspace['BCMx_Variant'] = 1
        self._data_port_updater()


    @staticmethod
    def _find_io_subsystem(result):
        if isinstance(result, (list, tuple)):
            if not result:
                return None
            return result[0]
        return result

    @staticmethod
    def _matlab_elements(elements):
        if elements is None:
            return []
        if isinstance(elements, str):
            return [elements] if elements else []
        try:
            return [str(element) for element in elements if str(element)]
        except TypeError:
            return [str(elements)] if str(elements) else []

    @staticmethod
    def _mapping_signals(mapping: dict) -> list[str]:
        metadata_keys = {"cluster", "ECU", "ecu", "dir", "type"}
        signals = []
        for key, value in mapping.items():
            if key in metadata_keys or value is None:
                continue
            if key not in signals:
                signals.append(key)
        return signals

    def _find_data_port_block(self, io_subsystem, block_name: str):
        data_port_block = self._find_io_subsystem(
            self.m_eng.find_system(io_subsystem, "Name", block_name, nargout=1)
        )
        if data_port_block is None:
            raise ValueError(f"Data port block '{block_name}' was not found.")
        return data_port_block

    def _ensure_signal(self, block_name: str, ecu: str, signal: str):
        data_port_block = self._dp_block[block_name]
        current_ecus = self._matlab_elements(
            self.m_eng.dsmpb_get(data_port_block, "port", "Elements", nargout=1)
        )

        if ecu not in current_ecus:
            logger.info("Adding %s/%s to %s", ecu, signal, block_name)
            self.m_eng.dsmpb_addsignal(data_port_block, ["port", ecu, signal], nargout=0)
            return

        current_signals = self._matlab_elements(
            self.m_eng.dsmpb_get(data_port_block, ["port", ecu], "Elements", nargout=1)
        )
        if signal not in current_signals:
            logger.info("Adding %s/%s to %s", ecu, signal, block_name)
            self.m_eng.dsmpb_addsignal(data_port_block, ["port", ecu, signal], nargout=0)

    def _data_port_updater(self):
        self.m_eng.openProject(self._m_prj_config.m_proj_path, nargout=0)
        
        io_subsystem = self._find_io_subsystem(
            self.m_eng.find_system(
                self._m_prj_config.io_mdl, "Name", self._m_prj_config.io_subsystem, nargout=1)
        )
        if io_subsystem is None:
            raise ValueError(f"IO subsystem '{self._m_prj_config.io_subsystem}' was not found.")
        
        for dpb_name in self._dp_name:
            self._dp_block[dpb_name] = self._find_data_port_block(io_subsystem, dpb_name)

        target_blocks = {
            "Sim": ["External_In", "Bus_Simulation"],
            "Ins": ["External_Out", "Bus_Inspection"],
        }

        for mapping in self._mapping_list or []:
            signal_dir = mapping.get("dir")
            ecu = mapping.get("ECU") or mapping.get("ecu")
            signals = self._mapping_signals(mapping)

            if signal_dir not in target_blocks:
                raise ValueError(f"Invalid mapping direction: {signal_dir}")
            if not ecu:
                raise ValueError(f"Mapping is missing ECU: {mapping}")

            for block_name in target_blocks[signal_dir]:
                for signal in signals:
                    self._ensure_signal(block_name, ecu, signal)
