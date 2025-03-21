import flask


class Server:
    def __init__(self, sdk):
        self.triggers: dict[str, list[object]] = {}
        self.serv = sdk.env.SERVER
        self.app = flask.Flask(__name__)

    def ShowTriggers(self) -> dict[str, list[object]]:
        return self.triggers

    def AddTrigger(self, trigger: object):
        t_name = trigger.on
        if t_name not in self.triggers:
            self.triggers[t_name] = []
        self.triggers[t_name].append(trigger)

    def Start(self):
        @self.app.route("/", methods=["POST"])
        def Handle():
            data = flask.request.json
            t_name = data["header"]["eventType"]
            for h in self.triggers[t_name]:
                h.OnRecv(data)
            return "OK"

        self.app.run(**self.serv)
