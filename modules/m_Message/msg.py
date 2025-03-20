class Message:
    def __init__(self, sdk):
        self.yhToken = sdk.MessageBase.yhToken
        self.NetJsonPost = sdk.MessageBase.NetJsonPost
        self.NetJsonGet = sdk.MessageBase.NetJsonGet