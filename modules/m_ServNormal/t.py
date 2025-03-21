class Trigger:
    def __init__(self, sdk):
        self.on = "message.receive.normal"
        self.handles: list[object] = []

    def ShowHandles(self):
        return self.handles

    def AddHandle(self, handle):
        self.handles.append(handle)

    def OnRecv(self, data):
        for handle in self.handles:
            handle(data)