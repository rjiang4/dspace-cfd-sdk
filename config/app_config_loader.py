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

RIGS = ["SYSINT", "DOMAIN", "ACTUATOR"]

def app_config_loader(yaml_path: Path, rig: str) -> ApplicationConfig:
    """load configuration for application"""

    logger.info(" Load configuration for application ")
    rig = rig.upper()
    
    if rig not in RIGS:
        logger.exception(f"Invalid rig type: {rig}, please choose from {RIGS}.")
        raise ValueError

    workspace_parent = Path(__file__).resolve().parents[2]

    def path_config(path: Path | str | None) -> str | None:
        if path is None:
            return None
        path = Path(path)
        if path.is_absolute():
            return str(path)
        return str(workspace_parent / path)

    logger.debug(f" Workspace parent path is: {str(workspace_parent)}")

    with open(yaml_path, "r") as f:
        raw_config = yaml.safe_load(f)
    
    common_config = raw_config["COMMON"]
    rig_config = raw_config["RIGS"][rig]
    mdl_config = common_config.get("MODEL") or {}
    
    final_config = common_config | rig_config
    final_config.update(mdl_config)
    
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
        rig_config.get("COMMUNICATION_MATRIX") or \
        common_config.get("COMMUNICATION_MATRIX")
    
    cfd_config = CfdConfig(
        cfd_proj_path=path_config(final_config["PROJECT_ROOT_PATH"]),
        cfd_proj_name=final_config["PROJECT_NAME"],
        cfd_app_name=final_config["APPLICATION_NAME"],
    )
            
    db_config = DbConfig(
        db_paths=[path_config(final_config["COMMUNICATION_MATRIX"])],
    )
    
    m_proj_config = MProjConfig(
        io_mdl=final_config["IO_MODEL"],
        io_subsystem=final_config["IO_SUBSYSTEM"],
        lkd_mdl=final_config["LINKED_MODEL"],
        lkd_subsystem_in=final_config["LINKED_SUBSYSTEM_IN"],
        lkd_dpb_in=final_config["LINKED_DPB_IN"],
        lkd_subsystem_out=final_config["LINKED_SUBSYSTEM_OUT"],
        lkd_dpb_out=final_config["LINKED_DPB_OUT"],
        
        m_proj_path=path_config(final_config['MODEL_PROJECT_PATH']),
    )
    
    bus_config = BmConfig(
        cluster=final_config['CLUSTER_LIST'],
        solution_cluster=final_config['SOLUTION_CLUSTER_LIST'],
        init_value=final_config['INITIAL_VALUE'],
        mapping_list=final_config['MAPPING_LIST'],
    )
    
    return ApplicationConfig(
        cfd_config=cfd_config,
        db_config=db_config,
        m_proj_config=m_proj_config,
        bus_config=bus_config
    )
    