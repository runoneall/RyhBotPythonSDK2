def init():

    import os
    import sys
    import json

    from . import util
    from . import errors
    from . import logger

    SimpleNamespace = type(sys.implementation)
    sdk = SimpleNamespace()

    if os.path.exists("./env.json"):
        print("Load env")
        with open("./env.json") as f:
            envJson = json.load(f)
        env = SimpleNamespace()
        for key, value in envJson.items():
            setattr(env, key, value)

        def envGet(key, default=None):
            return getattr(env, key, default)

        def envSet(key, value):
            setattr(env, key, value)

        setattr(env, "get", envGet)
        setattr(env, "set", envSet)
        setattr(sdk, "env", env)

    print("Load util")
    setattr(sdk, "util", util)
    setattr(sdk, "logger", logger.Logger("SDK"))

    sdkModulePath = os.path.join(os.path.dirname(__file__), "modules")
    sys.path.append(sdkModulePath)
    sdkInstalledModules: list[str] = [
        os.path.basename(x)
        for x in os.listdir(sdkModulePath)
        if os.path.isdir(os.path.join(sdkModulePath, x)) and x.startswith("m_")
    ]

    sdk.logger.info("Scan Dependencies")
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
        sdk.logger.info("Load {} -> {}".format(modulePackage, moduleInfo["name"]))
        if moduleInfo["name"] in dir(sdk):
            raise errors.InvalidModuleError(
                f"Module {modulePackage} has duplicate name"
            )
        if "Main" not in dir(module):
            raise errors.InvalidModuleError(f"Module {modulePackage} has no Main class")
        moduleLogger = logger.Logger(moduleInfo["name"])
        moduleMain: object = module.Main(sdk, moduleLogger)
        if hasattr(moduleMain, "install"):
            sdk = moduleMain.install(sdk)
        setattr(moduleMain, "moduleInfo", moduleInfo)
        setattr(sdk, moduleInfo["name"], moduleMain)
    return sdk
