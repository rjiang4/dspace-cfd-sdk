import logging
import argparse

from pathlib import Path

from logger.logger_config import logger_config
from app.controller import Controller

logger_config()

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="abs path of the rig specified yaml file")
    args = parser.parse_args()
    
    if args.path:
        yaml_path = Path(args.path)
        controller = Controller(yaml_path=yaml_path)
        
        controller.run()
        
    else:
        print("Need to specify a yaml file to continue...")
    