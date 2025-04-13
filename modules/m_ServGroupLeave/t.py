class Trigger:
    def __init__(self, sdk, logger):
        self.logger = logger
        self.on = "group.leave"
        self.handles: dict[list[object]] = {"ALL": []}

    def AddHandle(self, handle, uid="ALL"):
        self.logger.info(f"Add Handler {handle.__name__} With UID {uid}")
        if uid not in self.handles:
            self.handles[uid] = []
        self.handles[uid].append(handle)

    def OnRecv(self, data):
        uid = data["event"]["userId"]
        for handle in self.handles.get(uid, []):
            handle(data)
        for handle in self.handles.get("ALL", []):
            handle(data)
