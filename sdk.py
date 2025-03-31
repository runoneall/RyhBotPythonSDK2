if __name__ == "__main__":

    import os
    import util
    import json

    sdkModulePath = os.path.join(os.path.dirname(__file__), "modules")
    CmdArg = util.CmdArg()

    def checkEnvFile():
        if not os.path.exists("./env.json"):
            with open("./env.json", "w") as f:
                f.write("{}")

    def getEnvFile():
        with open("./env.json", "r") as f:
            return json.load(f)

    def getEnv(value):
        checkEnvFile()
        print(getEnvFile().get(value, None))

    CmdArg.Bind("-get-env", getEnv)

    def listEnv(value):
        checkEnvFile()
        for key, value in getEnvFile().items():
            print(key, "->", value)

    CmdArg.Bind("-list-env", listEnv)

    CmdArg.Execute()
