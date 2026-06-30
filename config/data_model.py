from dataclasses import dataclass
from pathlib import Path
    
@dataclass
class CfdConfig():
    """ConfigurationDesk prject property"""
    cfd_proj_path: Path
    cfd_proj_name: str
    cfd_app_name: str

@dataclass
class DbConfig():
    """Database property"""
    db_path: Path
    

@dataclass
class MProjConfig():
    """Matlab project property"""
    m_proj_path: Path
    m_proj_name: str
    m_script_path: Path
    asm_mdl_name: str
    io_mdl_name: str

@dataclass
class BmConfig():
    """BusManager property"""
    vcc_cluster: dict
    non_vcc_cluster: dict
    mapping_list: dict
    init_value: dict

@dataclass
class ApplicationConfig():
    """AutoConfig application configuration"""
    cfd_config: CfdConfig
    db_config: DbConfig
    m_proj_config: MProjConfig
    bus_config: BmConfig