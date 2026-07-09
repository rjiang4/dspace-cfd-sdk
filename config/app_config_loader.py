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

REPO_NAME = 'SVA_GPA_Simulation_opt'

def app_config_loader(yaml_path: Path) -> ApplicationConfig:
    """load configuration for application"""

    logger.info(" Load configuration for application ")

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
    
    cfd_config = CfdConfig(
        cfd_proj_path=path_config(raw_config['PROJECTROOTPATH']),
        cfd_proj_name=raw_config['PROJECTNAME'],
        cfd_app_name=raw_config['APPLICATIONNAME'],
    )
    
    db_paths=[path_config(raw_config['COMMUNICATIONMATRIXPATH'])]
    
    for cluster in raw_config['SOLCLUSTERLIST'] or []:
        if cluster.get("database"):
            db_paths.append(path_config(cluster.get("database")))
            
    db_config = DbConfig(
        db_paths=db_paths,
    )
    
    m_proj_config = MProjConfig(
        asm_mdl_name=raw_config['ASM_MODEL_NAME'],
        io_mdl_name=raw_config['IO_MODEL_NAME'],
        m_script_path=path_config(raw_config['M_SCRIPT_PATH']),
        m_proj_path=path_config(raw_config['MODEL_PROJECT_PATH']),
        m_proj_name=raw_config['MODEL_PROJECT_NAME'],
    )
    
    bus_config = BmConfig(
        vcc_cluster=raw_config['VCCCLUSTERLIST'],
        non_vcc_cluster=raw_config['SOLCLUSTERLIST'],
        init_value=raw_config['INITIAL_VALUE'],
        mapping_list=raw_config['MAPPING_LIST'],
    )
    
    return ApplicationConfig(
        cfd_config=cfd_config,
        db_config=db_config,
        m_proj_config=m_proj_config,
        bus_config=bus_config
    )
    