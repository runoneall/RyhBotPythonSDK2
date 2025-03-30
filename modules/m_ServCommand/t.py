class Trigger:
    def __init__(self, sdk):
        self.on = "message.receive.instruction"
        self.handles: dict[list[object]] = {"ALL": []}

    def AddHandle(self, handle, cmdid="ALL"):
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
