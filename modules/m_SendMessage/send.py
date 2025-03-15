class SendMessage:
    def __init__(self, sdk):
        self.token = sdk.MessageBase.yhToken
        self.NetJsonPost = sdk.MessageBase.NetJsonPost
    
    def print_token(self):
        print(self.token)