if __name__ == "__main__":

    import os
    import util

    sdkModulePath = os.path.join(os.path.dirname(__file__), "modules")
    CmdArg = util.CmdArg()

    def on_set_a(value):
        print("set a", value)
    
    def on_set_b(value):
        print("set b", value)
    
    def on_set_c(value):
        print("set c", value)
    
    CmdArg.Bind("--a", on_set_a)
    CmdArg.Bind("--b", on_set_b)
    CmdArg.Bind("--c", on_set_c)

    CmdArg.Execute()