# dspace-cfd-sdk

Automation SDK for configuring dSPACE ConfigurationDesk projects for HIL rigs.

The tool reads a rig-specific YAML file, opens or creates the configured ConfigurationDesk project/application, updates Matlab data ports, imports communication matrices, configures BusManager content, and applies signal mapping and initial values.

## Requirements

- Windows
- Python 3.11 or newer
- dSPACE ConfigurationDesk with COM automation support
- dSPACE Python COM package, including `dspace.com`
- pywin32, including `win32com` and `pywintypes`
- Matlab with the Matlab Engine API for Python
- PyYAML

Install the Python package dependency used by the config loader:

```powershell
python -m pip install PyYAML
```

If the app cannot import `yaml`, verify the terminal Python environment:

```powershell
python -c "import sys; print(sys.executable)"
python -c "import yaml; print(yaml.__version__)"
```

## Configuration

Create or update a YAML file under `data/`. See `data/SnsrSysInt.yaml` for a full example.

Important YAML sections:

- `PROJECTROOTPATH`, `PROJECTNAME`, `APPLICATIONNAME`: ConfigurationDesk project/application location and names.
- `COMMUNICATIONMATRIXPATH`: root folder for communication matrix files.
- `M_SCRIPT_PATH`, `MODEL_PROJECT_PATH`, `MODEL_PROJECT_NAME`: Matlab project/script inputs.
- `ASM_MODEL_NAME`, `IO_MODEL_NAME`: model names used for data port mapping.
- `VCCCLUSTERLIST`: primary bus clusters to configure.
- `SOLCLUSTERLIST`: optional additional solution/third-party clusters.
- `INITIAL_VALUE`: optional initial signal values.
- `MAPPING_LIST`: optional BusManager-to-model signal mapping.

Relative paths in the YAML are resolved from the repository parent path used by `config/app_config_loader.py`.

## Run

From the repository root:

```powershell
python main.py -p data\SnsrSysInt.yaml
```

You can also pass an absolute path:

```powershell
python main.py --path C:\path\to\rig_config.yaml
```

## Logs

Logs are written to the `log/` directory. Each run creates a timestamped file, for example:

```text
log/app_20260630_154324_170821.log
```

Logs are also printed to the console.

## Project Structure

```text
app/        Main application controller
config/     YAML loader and config dataclasses
data/       Example rig YAML files
logger/     Logging configuration
matlab/     Matlab helper scripts
service/    ConfigurationDesk, BusManager, IO, and Matlab services
lib/        Optional project-specific user code modules
```

## Quick Checks

Check that Python can import the basic runtime dependencies:

```powershell
python -c "import yaml; print(yaml.__version__)"
python -c "import win32com.client, pywintypes; print('pywin32 ok')"
```

Check syntax for the main Python modules:

```powershell
python -m py_compile main.py app\controller.py config\app_config_loader.py config\data_model.py logger\logger_config.py service\app_service.py service\bus_manager_service.py service\configuration_desk_service.py service\io_service.py service\matlab_service.py
```
