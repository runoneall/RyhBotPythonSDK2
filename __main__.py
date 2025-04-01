import os
import json
import sys
import shutil
import requests

from . import util

sdkModulePath = os.path.join(os.path.dirname(__file__), "modules")
sys.path.append(sdkModulePath)

CmdArg = util.CmdArg()


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
        v = v.split(":")[1]
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
    else:
        v = float(v)
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
        if os.path.isdir(os.path.join(sdkModulePath, x)) and x.startswith("m_")
    ]
    for module in sdkInstalledModules:
        print(module)


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
    print(f"Found {len(moduleFind)} modules:\n")
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
            print(f"  Optional: {', '.join(module['optional_dependencies'])}")
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
    if os.path.exists(os.path.join(sdkModulePath, targetModuleName)):
        if input(f"\n{targetModuleName} already installed. Overwrite? (y/n) ") == "y":
            shutil.rmtree(os.path.join(sdkModulePath, targetModuleName))
            shutil.move(
                os.path.join(targetPath, targetModuleName),
                os.path.join(sdkModulePath, targetModuleName),
            )
            print(f"Module {targetModuleName} installed.")
        else:
            print("Abort.")
    shutil.rmtree(targetPath)


CmdArg.Bind("-install-module", installModule)

CmdArg.OnError("Invalid command.")
CmdArg.Execute()
