import logging
import yaml
from pathlib import Path
from config.data_model import (
    ApplicationConfig,
    CfdConfig,
    DbConfig,
    MProjConfig,
    BmConfig
)

logger = logging.getLogger(__name__)

REPO_NAME = "SVA_GPA_Simulation_opt"
RIGS = ["SysInt", "Domain", "Actuator"]

def app_config_loader(yaml_path: Path, rig: str) -> ApplicationConfig:
    """load configuration for application"""

    logger.info(" Load configuration for application ")
    
    if rig not in RIGS:
        logger.exception(f"Invalid rig type: {rig}, please choose from {RIGS}.")
        raise ValueError

    yaml_path_parts = yaml_path.parts

    try:
        idx = yaml_path_parts.index(REPO_NAME)
    except ValueError:
        logger.exception(f"Repo {REPO_NAME} not found in path: {str(yaml_path)}, "
                         f"please put yaml file inside the repo.")
        raise

    repo_root = Path(*yaml_path_parts[:idx])

    def path_config(path: Path) -> str:
        return str(repo_root / Path(path))

    logger.debug(f" Repo root path is: {str(repo_root)}")

    with open(yaml_path, "r") as f:
        raw_config = yaml.safe_load(f)
    
    common_config = raw_config["COMMON"]
    rig_config = raw_config["RIGS"][rig.upper()]
    
    final_config = common_config | rig_config
    
    final_config["CLUSTER_LIST"] = \
        (common_config.get("CLUSTER_LIST") or []) + \
        (rig_config.get("CLUSTER_LIST") or [])
        
    final_config["SOLUTION_CLUSTER_LIST"] = \
        (common_config.get("SOLUTION_CLUSTER_LIST") or []) + \
        (rig_config.get("SOLUTION_CLUSTER_LIST") or [])

    final_config["INITIAL_VALUE"] = \
        (common_config.get("INITIAL_VALUE") or []) + \
        (rig_config.get("INITIAL_VALUE") or [])
        
    final_config["MAPPING_LIST"] = \
        (common_config.get("MAPPING_LIST") or []) + \
        (rig_config.get("MAPPING_LIST") or [])
        
    final_config["COMMUNICATION_MATRIX"] = \
        (common_config.get("COMMUNICATION_MATRIX") or []) + \
        (rig_config.get("COMMUNICATION_MATRIX") or [])
    
    
    cfd_config = CfdConfig(
        cfd_proj_path=path_config(final_config["PROJECT_ROOT_PATH"]),
        cfd_proj_name=final_config["PROJECT_NAME"],
        cfd_app_name=final_config["APPLICATION_NAME"],
    )
            
    db_config = DbConfig(
        db_paths=[path_config(final_config["COMMUNICATION_MATRIX"])],
    )
    
    m_proj_config = MProjConfig(
        asm_mdl_name=final_config['ASM_MODEL_NAME'],
        io_mdl_name=final_config['IO_MODEL_NAME'],
        m_script_path=path_config(final_config['M_SCRIPT_PATH']),
        m_proj_path=path_config(final_config['MODEL_PROJECT_PATH']),
        m_proj_name=final_config['MODEL_PROJECT_NAME'],
    )
    
    bus_config = BmConfig(
        vcc_cluster=final_config['VCC_CLUSTER_LIST'],
        non_vcc_cluster=final_config['SOLUTION_CLUSTER_LIST'],
        init_value=final_config['INITIAL_VALUE'],
        mapping_list=final_config['MAPPING_LIST'],
    )
    
    return ApplicationConfig(
        cfd_config=cfd_config,
        db_config=db_config,
        m_proj_config=m_proj_config,
        bus_config=bus_config
    )
    