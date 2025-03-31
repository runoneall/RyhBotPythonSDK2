class Trigger:
    def __init__(self, sdk, logger):
        self.on = "message.receive.instruction"
        self.handles: dict[list[object]] = {"ALL": []}
        self.logger = logger

    def AddHandle(self, handle, cmdid="ALL"):
        self.logger.info(f"Add Handler {handle.__name__} With Command {cmdid}")
        if cmdid not in self.handles:
            self.handles[cmdid] = []
        self.handles[cmdid].append(handle)

    def OnRecv(self, data):
        if "instructionId" in data["event"]["message"]:
            cmdid = data["event"]["message"]["instructionId"]
        else:
            cmdid = data["event"]["message"]["commandId"]
        for handle in self.handles.get(cmdid, []):
            handle(data)
        for handle in self.handles.get("ALL", []):
            handle(data)
