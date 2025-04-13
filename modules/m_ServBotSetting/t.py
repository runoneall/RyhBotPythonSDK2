class Trigger:
    def __init__(self, sdk, logger):
        self.logger = logger
        self.on = "bot.setting"
        self.handles: dict[list[object]] = {"ALL": []}

    def AddHandle(self, handle, gid="ALL"):
        self.logger.info(f"Add Handler {handle.__name__} With Group {gid}")
        if gid not in self.handles:
            self.handles[gid] = []
        self.handles[gid].append(handle)

    def OnRecv(self, data):
        gid = data["event"]["groupId"]
        for handle in self.handles.get(gid, []):
            handle(data)
        for handle in self.handles.get("ALL", []):
            handle(data)
