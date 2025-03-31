if __name__ == "__main__":

    import os
    import util
    import json
    import requests

    sdkModulePath = os.path.join(os.path.dirname(__file__), "modules")
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

    # For Origins
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
        moduleObj["moduleAlias"] = {}
        for origin in origins:
            print(f"Fetch {origin}")
            content = requests.get(origin).json()
            moduleObj["providers"][content["name"]] = content["base"]
            for module in list(content["modules"].keys()):
                moduleContent = content["modules"][module]
                moduleObj["modules"][f'{module}@{content["name"]}'] = moduleContent
                moduleOriginName = moduleContent["path"][1:-4]
                moduleAliasName = module
                moduleObj["moduleAlias"][
                    f'{moduleOriginName}@{content["name"]}'
                ] = moduleAliasName
        writeModuleFile(moduleObj)
        print("done")

    CmdArg.Bind("-update-origin", updateOrigin)

    CmdArg.OnError("Invalid command.")
    CmdArg.Execute()
