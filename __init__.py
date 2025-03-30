import os
import sys

from . import sdk
from . import util
from . import errors
from . import logger

if os.path.exists("./env.py"):
    print("Load env")
    setattr(sdk, "env", __import__("env"))
print("Load util")
setattr(sdk, "util", util)
setattr(sdk, "logger", logger.logger)

sdkModulePath = os.path.join(os.path.dirname(__file__), "modules")
sys.path.append(sdkModulePath)
sdkInstalledModules: list[str] = [
    os.path.basename(x)
    for x in os.listdir(sdkModulePath)
    if os.path.isdir(os.path.join(sdkModulePath, x)) and x.startswith("m_")
]

sdkModuleDependencies = {}
for module in sdkInstalledModules:
    moduleDependecies: list[str] = __import__(module).moduleInfo["dependencies"]
    if not all(dep in sdkInstalledModules for dep in moduleDependecies):
        raise errors.InvalidDependencyError(
            f"Invalid module dependency for module {module}: {moduleDependecies}"
        )
    sdkModuleDependencies[module] = moduleDependecies
sdkInstalledModules: list[object] = [
    __import__(m)
    for m in sdk.util.topological_sort(
        sdkInstalledModules, sdkModuleDependencies, errors.CycleDependencyError
    )
]

for module in sdkInstalledModules:
    modulePackage: str = module.__package__
    moduleInfo: dict = module.moduleInfo
    print("Load {} -> {}".format(modulePackage, moduleInfo["name"]))
    if moduleInfo["name"] in dir(sdk):
        raise errors.InvalidModuleError(f"Module {modulePackage} has duplicate name")
    if "Main" not in dir(module):
        raise errors.InvalidModuleError(f"Module {modulePackage} has no Main class")
    moduleMain: object = module.Main(sdk)
    setattr(moduleMain, "moduleInfo", moduleInfo)
    setattr(sdk, moduleInfo["name"], moduleMain)
