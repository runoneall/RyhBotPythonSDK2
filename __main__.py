import os
import json
import sys
import shutil
import zipfile
import requests


class CmdArg:
    def __init__(self):
        self.cmdArgs: list[str] = sys.argv[1:]
        self.bindArgs: list[str] = []
        self.bindArgObjs: dict[str, object] = {}
        self.error = ""
        self.errorFlag = True

    def Bind(self, argName: str, argObj: object):
        self.bindArgs.append(argName)
        self.bindArgObjs[argName] = argObj

    def OnError(self, error):
        self.error = error

    def Execute(self):
        for i in range(len(self.cmdArgs)):
            arg = self.cmdArgs[i]
            if arg not in self.bindArgs:
                continue
            if (
                self.cmdArgs[i] == self.cmdArgs[-1]
                or self.cmdArgs[i + 1] in self.bindArgs
            ):
                value = ""
            else:
                value = self.cmdArgs[i + 1]
            self.bindArgObjs[arg](value)
            self.errorFlag = False
        if self.errorFlag:
            print(self.error)
            exit(1)


def compare_versions(version1: str, version2: str) -> int:
    v1 = list(map(int, version1.split(".")))
    v2 = list(map(int, version2.split(".")))
    for i in range(max(len(v1), len(v2))):
        num1 = v1[i] if i < len(v1) else 0
        num2 = v2[i] if i < len(v2) else 0
        if num1 > num2:
            return 1
        elif num1 < num2:
            return -1
    return 0


sdkModulePath = os.path.join(os.path.dirname(__file__), "modules")
sys.path.append(sdkModulePath)
CmdArg = CmdArg()


# For Env
def checkEnvFile():
    if not os.path.exists("./env.json"):
        with open("./env.json", "w") as f:
            f.write("{}")


def getEnvFile():
    with open("./env.json", "r") as f:
        return json.load(f)


def writeEnvFile(envObj):
    with open("./env.json", "w") as f:
        json.dump(envObj, f, indent=2)


def getEnv(value):
    checkEnvFile()
    print(getEnvFile().get(value, None))


CmdArg.Bind("-get-env", getEnv)


def listEnv(value):
    checkEnvFile()
    for key, value in getEnvFile().items():
        print(key, "->", value)


CmdArg.Bind("-list-env", listEnv)


def setEnv(value):
    checkEnvFile()
    k = value.split("=")[0]
    v = value.split("=")[1]
    if ":" in v:
        v_type = v.split(":")[0]
        v = ':'.join(v.split(":")[1:])
    else:
        v_type = "str"

    if v_type == "int":
        v = int(v)
    elif v_type == "str":
        v = str(v)
    elif v_type == "bool":
        if v == "true":
            v = True
        else:
            v = False
    elif v_type == "float":
        v = float(v)
    elif v_type == "json":
        v = json.loads(v)
    else:
        print(f"Invalid type {v_type}")
        exit(1)
    writeEnvFile({**getEnvFile(), **{k: v}})


CmdArg.Bind("-set-env", setEnv)


def delEnv(value):
    checkEnvFile()
    origin_env = getEnvFile()
    del origin_env[value]
    writeEnvFile(origin_env)


CmdArg.Bind("-del-env", delEnv)


# For Origin
def checkModuleFile():
    if not os.path.exists("./module.json"):
        with open("./module.json", "w") as f:
            f.write('{\n    "origins": []\n}')


def getModuleFile():
    with open("./module.json", "r") as f:
        return json.load(f)


def writeModuleFile(moduleObj):
    with open("./module.json", "w") as f:
        json.dump(moduleObj, f, indent=2, ensure_ascii=False)


def addOrigin(value):
    checkModuleFile()
    moduleObj = getModuleFile()
    if value not in moduleObj["origins"]:
        moduleObj["origins"].append(value)
        writeModuleFile(moduleObj)


CmdArg.Bind("-add-origin", addOrigin)


def updateOrigin(value):
    checkModuleFile()
    moduleObj = getModuleFile()
    origins = moduleObj["origins"]
    moduleObj["providers"] = {}
    moduleObj["modules"] = {}
    for origin in origins:
        print(f"Fetch {origin}")
        content = requests.get(origin, headers={"User-Agent": "SDK Frame CLI"}).json()
        moduleObj["providers"][content["name"]] = content["base"]
        for module in list(content["modules"].keys()):
            moduleContent = content["modules"][module]
            moduleObj["modules"][f'{module}@{content["name"]}'] = moduleContent
    writeModuleFile(moduleObj)
    print("done")


CmdArg.Bind("-update-origin", updateOrigin)


def listOrigin(value):
    checkModuleFile()
    moduleObj = getModuleFile()
    for origin in moduleObj["origins"]:
        print(origin)


CmdArg.Bind("-list-origin", listOrigin)


def delOrigin(value):
    checkModuleFile()
    moduleObj = getModuleFile()
    if value in moduleObj["origins"]:
        moduleObj["origins"].remove(value)
        writeModuleFile(moduleObj)


CmdArg.Bind("-del-origin", delOrigin)


# For Module
def checkModuleDir():
    if not os.path.exists(sdkModulePath):
        os.makedirs(sdkModulePath)


def checkModuleExist(module):
    checkModuleDir()
    return os.path.exists(os.path.join(sdkModulePath, module))


def checkInstallDir(targetPath):
    if os.path.exists(targetPath):
        shutil.rmtree(targetPath)
    os.mkdir(targetPath)


def listModule(value):
    checkModuleDir()
    sdkInstalledModules: list[str] = [
        os.path.basename(x)
        for x in os.listdir(sdkModulePath)
        if os.path.isdir(os.path.join(sdkModulePath, x))
    ]
    for module in sdkInstalledModules:
        if module.startswith("m_"):
            print(module)
        if module.startswith("dm_"):
            print(module[1:], "(disabled)")


CmdArg.Bind("-list-module", listModule)


def moduleInfo(value):
    if not checkModuleExist(value):
        print(f"Module {value} not found.")
        exit(1)
    moduleInfo = __import__(value).moduleInfo
    print(f"NameSpace: sdk.{moduleInfo['name']}")
    print(f"Author: {moduleInfo['author']}")
    print(f"Version: {moduleInfo['version']}")
    print(f"\n  {moduleInfo['description']}\n")
    if "dependencies" in moduleInfo and len(moduleInfo["dependencies"]) > 0:
        print(f"Dependencies: {', '.join(moduleInfo['dependencies'])}")
    if (
        "optional_dependencies" in moduleInfo
        and len(moduleInfo["optional_dependencies"]) > 0
    ):
        print(
            f"Optional Dependencies: {', '.join(moduleInfo['optional_dependencies'])}"
        )


CmdArg.Bind("-module-info", moduleInfo)


def enableModule(value):
    checkModuleDir()
    if os.path.exists(os.path.join(sdkModulePath, value)):
        print(f"Module {value} already enabled.")
        return
    os.rename(
        os.path.join(sdkModulePath, f"d{value}"), os.path.join(sdkModulePath, value)
    )
    print(f"Module {value} enabled.")


CmdArg.Bind("-enable-module", enableModule)


def disableModule(value):
    checkModuleDir()
    if os.path.exists(os.path.join(sdkModulePath, f"d{value}")):
        print(f"Module {value} already disabled.")
        return
    os.rename(
        os.path.join(sdkModulePath, value), os.path.join(sdkModulePath, f"d{value}")
    )
    print(f"Module {value} disabled.")


CmdArg.Bind("-disable-module", disableModule)


def delModule(value):
    if not checkModuleExist(value):
        print(f"Module {value} already deleted.")
        return
    shutil.rmtree(os.path.join(sdkModulePath, value))
    print(f"Module {value} deleted.")


CmdArg.Bind("-del-module", delModule)


def installModule(value):
    checkModuleDir()
    checkModuleFile()
    if value == "":
        print("Please input module name.")
        exit(1)
    moduleObj = getModuleFile()
    moduleFind = [
        x for x in list(moduleObj["modules"].keys()) if value.lower() in x.lower()
    ]
    if len(moduleFind) == 0:
        print(f"No module match {value}.")
        exit(1)
    print(f"Found {len(moduleFind)} modules for {value}:\n")
    for item in moduleFind:
        print(f"- {item}")
        module = moduleObj["modules"][item]
        print(f"  Version: {module['version']}")
        print(f"  Author: {module['author']}")
        print(f"  {module['description']}")
        if "dependencies" in module and len(module["dependencies"]) > 0:
            print(f"  Dependencies: {', '.join(module['dependencies'])}")
        if (
            "optional_dependencies" in module
            and len(module["optional_dependencies"]) > 0
        ):
            print("  Optional: ", end="")
            for opt_dep in module["optional_dependencies"]:
                if type(opt_dep) == str:
                    print(f"{opt_dep} ", end="")
                if type(opt_dep) == list:
                    print(f"({' | '.join(opt_dep)}) ", end="")
            print("")
        print("")
    targetModule = input("You want install: ")
    if targetModule == "" or targetModule not in moduleFind:
        print("Please input target module name.")
        exit(1)
    print(f"\nInstalling {targetModule}...")
    targetPath = os.path.join(sdkModulePath, "INSTALL")
    checkInstallDir(targetPath)
    moduleUrl = (
        moduleObj["providers"][targetModule.split("@")[1]]
        + moduleObj["modules"][targetModule]["path"]
    )
    print(f"Fetch {moduleUrl}...")
    response = requests.get(
        moduleUrl, headers={"User-Agent": "SDK Frame CLI"}, stream=True
    )
    with open(os.path.join(targetPath, "module.zip"), "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print("Extracting...")
    shutil.unpack_archive(os.path.join(targetPath, "module.zip"), targetPath)
    os.remove(os.path.join(targetPath, "module.zip"))
    targetModuleName = [
        x for x in os.listdir(targetPath) if os.path.isdir(os.path.join(targetPath, x))
    ][0]
    if not targetModuleName.startswith("m_"):
        os.rename(
            os.path.join(targetPath, targetModuleName),
            os.path.join(targetPath, "m_" + targetModuleName),
        )
        targetModuleName = "m_" + targetModuleName
    if os.path.exists(os.path.join(sdkModulePath, targetModuleName)) or os.path.exists(
        os.path.join(sdkModulePath, "d" + targetModuleName)
    ):
        if input(f"\n{targetModuleName} already installed. Overwrite? (y/n) ") == "y":
            if os.path.exists(os.path.join(sdkModulePath, "d" + targetModuleName)):
                os.rename(
                    os.path.join(sdkModulePath, "d" + targetModuleName),
                    os.path.join(sdkModulePath, targetModuleName),
                )
            shutil.rmtree(os.path.join(sdkModulePath, targetModuleName))
        else:
            print("Abort.")
            shutil.rmtree(targetPath)
            return
    shutil.move(
        os.path.join(targetPath, targetModuleName),
        os.path.join(sdkModulePath, targetModuleName),
    )
    print(f"Module {targetModuleName} installed.")
    shutil.rmtree(targetPath)
    print("\nScan Dependencies...")
    targetModuleObj = moduleObj["modules"][targetModule]
    if "dependencies" in targetModuleObj and len(targetModuleObj["dependencies"]) > 0:
        print(
            "  Need {} dependencies: {}".format(
                len(targetModuleObj["dependencies"]),
                " ".join(targetModuleObj["dependencies"]),
            )
        )
        if input("Install? (y/n) ") == "y":
            for dep in targetModuleObj["dependencies"]:
                if dep.startswith("m_"):
                    dep = dep[2:]
                installModule(dep)
    if (
        "optional_dependencies" in targetModuleObj
        and len(targetModuleObj["optional_dependencies"]) > 0
    ):
        print("  Module has optional dependencies: ", end="")
        for opt_dep in targetModuleObj["optional_dependencies"]:
            if type(opt_dep) == str:
                print(f"{opt_dep} ", end="")
            if type(opt_dep) == list:
                print(f"({' | '.join(opt_dep)}) ", end="")
        print("\n  You can install them anytime.")
    print("Done.")


CmdArg.Bind("-install-module", installModule)


def loadModuleZip(value):
    checkModuleDir()
    if not os.path.exists(value):
        print(f"File {value} not found.")
        exit(1)
    targetPath = os.path.join(sdkModulePath, "INSTALL")
    checkInstallDir(targetPath)
    print(f"Extracting {value}...")
    shutil.unpack_archive(value, targetPath)
    targetModuleName = [
        x for x in os.listdir(targetPath) if os.path.isdir(os.path.join(targetPath, x))
    ][0]
    if not targetModuleName.startswith("m_"):
        os.rename(
            os.path.join(targetPath, targetModuleName),
            os.path.join(targetPath, "m_" + targetModuleName),
        )
        targetModuleName = "m_" + targetModuleName
    if os.path.exists(os.path.join(sdkModulePath, targetModuleName)) or os.path.exists(
        os.path.join(sdkModulePath, "d" + targetModuleName)
    ):
        if input(f"\n{targetModuleName} already installed. Overwrite? (y/n) ") == "y":
            if os.path.exists(os.path.join(sdkModulePath, "d" + targetModuleName)):
                os.rename(
                    os.path.join(sdkModulePath, "d" + targetModuleName),
                    os.path.join(sdkModulePath, targetModuleName),
                )
            shutil.rmtree(os.path.join(sdkModulePath, targetModuleName))
        else:
            print("Abort.")
            shutil.rmtree(targetPath)
            return
    shutil.move(
        os.path.join(targetPath, targetModuleName),
        os.path.join(sdkModulePath, targetModuleName),
    )
    print(f"Module {targetModuleName} installed.")
    shutil.rmtree(targetPath)


CmdArg.Bind("-load-zip", loadModuleZip)


def checkUpgrade(value):
    checkModuleDir()
    checkModuleFile()
    updateOrigin("")
    sdkInstalledModules: list[object] = [
        __import__(x)
        for x in os.listdir(sdkModulePath)
        if os.path.isdir(os.path.join(sdkModulePath, x)) and x.startswith("m_")
    ]
    moduleObj = getModuleFile()
    moduleDict: dict = moduleObj["modules"]
    moduleList: list = list(moduleDict.keys())
    upgradeList: dict = {}
    for module in sdkInstalledModules:
        modulePackage: str = module.__package__[2:]
        moduleVersion: str = module.moduleInfo["version"]
        upgradeCandidates: list = [
            x for x in moduleList if x.split("@")[0] == modulePackage
        ]
        targetCandidate: str = upgradeCandidates[0]
        if len(upgradeCandidates) > 1:
            print(f"Module {modulePackage} has more than one provider.\n")
            for candidate in upgradeCandidates:
                print(f"  {candidate}")
            targetCandidate = input("\nYou want use: ")
            if targetCandidate not in upgradeCandidates:
                print("Invalid input.")
                exit(1)
        if moduleDict[targetCandidate]["version"] != moduleVersion:
            if (
                compare_versions(moduleVersion, moduleDict[targetCandidate]["version"])
                == -1
            ):
                upgradeList[modulePackage] = targetCandidate
    if len(upgradeList) == 0:
        print("All modules are up to date.")
        return
    print(f"Found {len(upgradeList)} modules need upgrade:\n")
    for module, target in upgradeList.items():
        print(f"  {target}: {moduleVersion} -> {moduleDict[target]["version"]}")
    if input("\nUpgrade? (y/n) ") == "y":
        targetPath = os.path.join(sdkModulePath, "INSTALL")
        for module, target in upgradeList.items():
            print(f"\nUpgrading {module}...")
            checkInstallDir(targetPath)
            moduleUrl = (
                moduleObj["providers"][target.split("@")[1]]
                + moduleDict[target]["path"]
            )
            print(f"Fetch {moduleUrl}...")
            response = requests.get(
                moduleUrl, headers={"User-Agent": "SDK Frame CLI"}, stream=True
            )
            with open(os.path.join(targetPath, "module.zip"), "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print("Extracting...")
            shutil.unpack_archive(os.path.join(targetPath, "module.zip"), targetPath)
            os.remove(os.path.join(targetPath, "module.zip"))
            targetModuleName = [
                x
                for x in os.listdir(targetPath)
                if os.path.isdir(os.path.join(targetPath, x))
            ][0]
            if not targetModuleName.startswith("m_"):
                os.rename(
                    os.path.join(targetPath, targetModuleName),
                    os.path.join(targetPath, "m_" + targetModuleName),
                )
                targetModuleName = "m_" + targetModuleName
            shutil.rmtree(os.path.join(sdkModulePath, targetModuleName))
            shutil.move(
                os.path.join(targetPath, targetModuleName),
                os.path.join(sdkModulePath, targetModuleName),
            )
            print(f"Module {module} upgraded.")
        shutil.rmtree(targetPath)
        print("Done.")


CmdArg.Bind("-check-upgrade", checkUpgrade)


# For Persional Origin
checkOriginDir = checkInstallDir


def zip_dir(src_dir, dst_zip):
    base_dir = os.path.normpath(src_dir)
    main_folder = os.path.basename(base_dir)
    with zipfile.ZipFile(dst_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            files = [f for f in files if not f.startswith(".")]
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for file in files:
                file_path = os.path.join(root, file)
                parent_dir = os.path.dirname(base_dir)
                arcname_rel = os.path.relpath(file_path, parent_dir)
                arcname = os.path.join(
                    main_folder, os.path.relpath(file_path, base_dir)
                )
                zipf.write(file_path, arcname)


def makeOrigin(value):
    checkModuleFile()
    targetPath = os.path.join(".", "origin-release")
    checkOriginDir(targetPath)
    if not os.path.exists(os.path.join(".", "origin-maker-config.json")):
        with open(os.path.join(".", "origin-maker-config.json"), "w") as f:
            f.write(
                json.dumps(
                    {
                        "name": input("Origin Name: "),
                        "base": input("Origin Base URL: "),
                    },
                    indent=2,
                )
            )
    with open(os.path.join(".", "origin-maker-config.json"), "r") as f:
        origin_config = json.loads(f.read())
    origin_modules = {}
    sdkInstalledModules: list[str] = [
        os.path.basename(x)
        for x in os.listdir(sdkModulePath)
        if os.path.isdir(os.path.join(sdkModulePath, x)) and x.startswith("m_")
    ]
    for module in sdkInstalledModules:
        print(f"Add {module} to origin...")
        moduleInfo: dict = __import__(module).moduleInfo
        origin_module_body = moduleInfo.copy()
        del origin_module_body["name"]
        origin_module_body["path"] = f"/{module}.zip"
        origin_modules[moduleInfo["name"]] = origin_module_body
        zip_dir(
            os.path.join(sdkModulePath, module),
            os.path.join(targetPath, f"{module}.zip"),
        )
    print(f"Make map.json...")
    origin_map = {**origin_config, **{"modules": origin_modules}}
    with open(os.path.join(targetPath, "map.json"), "w") as f:
        json.dump(origin_map, f, indent=2, ensure_ascii=False)
    print(f"Make origin release at {targetPath}.")


CmdArg.Bind("-make-origin", makeOrigin)


def showHelp(value):
    print(
        """
SDK Frame CLI Usage:

  For Env:
    -set-env <key> [<type>:]<value>  Set environment variable. <type> can be "str", "int", "float", "bool", "json".
    -del-env <key>                   Delete environment variable.
    -list-env                        List all environment variables.

  For Origin:
    -add-origin <origin>             Add origin to module.json file.
    -update-origin                   Update origin list in module.json file.
    -list-origin                     List all origins in module.json file.
    -del-origin <origin>             Delete origin from module.json file.
    -make-origin                     Make origin release.

  For Module:
    -list-module                     List all installed modules.
    -module-info <module>            Show module information.
    -enable-module <module>          Enable module.
    -disable-module <module>         Disable module.
    -del-module <module>             Delete module.
    -install-module <module>         Install module.
    -load-zip <zipfile>              Install module from zip file.
    -check-upgrade                   Check and upgrade all modules.
"""
    )


CmdArg.Bind("-help", showHelp)

CmdArg.OnError("Invalid command.")
CmdArg.Execute()
