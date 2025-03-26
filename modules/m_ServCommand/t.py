class Trigger:
    def __init__(self, sdk):
        self.on = "message.receive.instruction"
        self.handles: list[object] = []

    def AddHandle(self, handle):
        self.handles.append(handle)

    def OnRecv(self, data):
        for handle in self.handles:
            handle(data)
