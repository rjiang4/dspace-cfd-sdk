import logging
import argparse

from pathlib import Path

from logger.logger_config import logger_config

logger_config()

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="abs path of the rig specified yaml file")
    parser.add_argument("-c", "--clusters", nargs="+", help="one or more cluster names")
    args = parser.parse_args()
    
    if args.path:
        from app.controller import Controller

        yaml_path = Path(args.path)
        clusters = args.clusters if args.clusters else []
        controller = Controller(yaml_path=yaml_path, clusters=clusters)
        
        controller.run()
        
    else:
        print("Need to specify a yaml file to continue...")
    