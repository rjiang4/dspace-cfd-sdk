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

ROOT_LEVEL = 4
REPO_ROOT = Path(__file__).resolve()

for _ in range(ROOT_LEVEL):
    REPO_ROOT = REPO_ROOT.parent

def path_config(path: Path) -> str:
    return str(REPO_ROOT / Path(path))

def app_config_loader(yaml_path: Path) -> ApplicationConfig:
    """load configuration for application"""

    logger.info(" Load configuration for application ")
    logger.debug(f" Repo root path is: {str(REPO_ROOT)}")

    with open(yaml_path, "r") as f:
        raw_config = yaml.safe_load(f)
    
    cfd_config = CfdConfig(
        cfd_proj_path=path_config(raw_config['PROJECTROOTPATH']),
        cfd_proj_name=raw_config['PROJECTNAME'],
        cfd_app_name=raw_config['APPLICATIONNAME'],
    )
    
    db_config = DbConfig(
        db_path=path_config(raw_config['COMMUNICATIONMATRIXPATH']),
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
    