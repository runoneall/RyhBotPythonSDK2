class SendMessage:
    def __init__(self, sdk):
        self.token = sdk.MessageBase.yhToken
    
    def print_token(self):
        print(self.token)