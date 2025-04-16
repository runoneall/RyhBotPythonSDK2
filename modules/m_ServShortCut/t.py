class Trigger:
    def __init__(self, sdk, logger):
        self.logger = logger
        self.on = "bot.shortcut.menu"
        self.handles: dict[list[object]] = {"ALL": []}

    def AddHandle(self, handle, mid="ALL"):
        self.logger.info(f"Add Handler {handle.__name__} With mid {mid}")
        if mid not in self.handles:
            self.handles[mid] = []
        self.handles[mid].append(handle)

    def OnRecv(self, data):
        mid = data["event"]["menuId"]
        for handle in self.handles.get(mid, []):
            handle(data)
        for handle in self.handles.get("ALL", []):
            handle(data)
