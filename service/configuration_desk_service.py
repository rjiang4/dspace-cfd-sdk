from win32com.client import Dispatch
from dspace.com import Enums
import logging
from pathlib import Path

from config.data_model import ApplicationConfig

logger = logging.getLogger(__name__)

class ConfigurationDeskService():
    def __init__(self, app_config: ApplicationConfig):
        
        self.cfd_app = None
        self.proj_root_path = None
        self.active_proj = None
        self.active_app = None
        self.app_config = app_config


    def dispatch_cfd(self, is_visible: bool = True):
        """ Dispatch the ConfigurationDesk application """

        self.cfd_app = Dispatch("ConfigurationDesk.Application")
        if is_visible:
            logger.debug(" Visualize the GUI ")
            self.Enums = Enums(self.cfd_app)
            self.cfd_app.MainWindow.Visible = is_visible
            self.cfd_app.MainWindow.State = self.Enums.MainWindowState.Maximized
            
    def start_cfd_project(self, cfd_proj_path: Path = None, cfd_proj_name: str = None):
        """ Start the CFD project
            If the project root/project name is not specified, it will use the one from the application configuration.
            If the project root/project is not existing, it will create a new one
        """
        
        if self.cfd_app is None:
            self.dispatch_cfd()
        
        if cfd_proj_path is None:
            cfd_proj_path = self.app_config.cfd_config.cfd_proj_path
        
        if cfd_proj_name is None:
            cfd_proj_name = self.app_config.cfd_config.cfd_proj_name
        
        # Specify or create project root.
        if self.cfd_app.ProjectRoots.Contains(cfd_proj_path):
            logger.info(f"Activate project from path: {cfd_proj_path}")
            self.proj_root_path = self.cfd_app.ProjectRoots.Item(cfd_proj_path)
            self.proj_root_path.Activate()
        else:
            logger.info(f"Creating and activating project root: {cfd_proj_path}") 
            self.proj_root_path = self.cfd_app.ProjectRoots.Add(cfd_proj_path)
            self.proj_root_path.Activate()
            
        # Specify or create project.
        if self.proj_root_path.Projects.Contains(cfd_proj_name):
            logger.info("Activating project...")
            self.active_proj = self.proj_root_path.Projects.Item(cfd_proj_name).Open(True)
        else:
            logger.info("Creating project...")
            self.active_proj = self.proj_root_path.Projects.Add(cfd_proj_name)
            

    def start_cfd_application(self, cfd_app_name: str = None):
        """ Start the CFD application
            If the project name is not specified, it will use the one from the application configuration.
            If the project name is not existing, it will create a new one
            If the application name is not specified, it will use the one from the application configuration.
            If the application name is not existing, it will create a new one
        """
        if self.active_proj is None:
            raise ValueError("Project is not specified. Please start a project first.")
        
        if cfd_app_name is None:
            cfd_app_name = self.app_config.cfd_config.cfd_app_name

        # Specify or create application.
        if self.active_proj.Applications.Contains(cfd_app_name):
            logger.info(f"Activating Application: {cfd_app_name}")
            self.active_app = self.active_proj.Applications.Item(cfd_app_name).Activate(True)
        else:
            logger.info(f"Creating Application: {cfd_app_name}")
            self.active_app = self.active_proj.Applications.Add(cfd_app_name)
    