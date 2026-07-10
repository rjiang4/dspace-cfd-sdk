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
    db_paths: list[Path]
    

@dataclass
class MProjConfig():
    """Matlab project property"""
    m_proj_path: Path
    io_mdl: str
    io_subsystem: str
    lkd_mdl: str | None
    lkd_subsystem_in: str | None
    lkd_dpb_in: str | None
    lkd_subsystem_out: str | None
    lkd_dpb_out: str | None

@dataclass
class BmConfig():
    """BusManager property"""
    cluster: list
    solution_cluster: list
    mapping_list: list
    init_value: list

@dataclass
class ApplicationConfig():
    """AutoConfig application configuration"""
    cfd_config: CfdConfig
    db_config: DbConfig
    m_proj_config: MProjConfig
    bus_config: BmConfig