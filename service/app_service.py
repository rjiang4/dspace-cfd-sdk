from service.configuration_desk_service import ConfigurationDeskService
from service.bus_manager_service import BusManagerService
from service.matlab_service import MatlabService
from service.io_service import IoService

from config.data_model import ApplicationConfig

class ApplicationService:
    def __init__(self, app_config: ApplicationConfig):
        self.configuration_desk_service = ConfigurationDeskService(app_config=app_config)
        self.configuration_desk_service.dispatch_cfd(is_visible=True)
        self.configuration_desk_service.start_cfd_project()
        self.configuration_desk_service.start_cfd_application()
        
        self.bus_manager_service = BusManagerService(configuration_desk_service=self.configuration_desk_service)
        
        self.matlab_service = MatlabService(app_config=app_config)
        
        self.io_service = IoService(configuration_desk_service=self.configuration_desk_service)

        self.ConfigurationDeskService = self.configuration_desk_service
        self.BusManagerService = self.bus_manager_service
        self.MatlabService = self.matlab_service
        self.IoService = self.io_service
