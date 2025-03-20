class Message:
    def __init__(self, sdk):
        self.yhToken = sdk.MessageBase.yhToken
        self.NetJsonPost = sdk.MessageBase.NetJsonPost
        self.NetJsonGet = sdk.MessageBase.NetJsonGet
        self.recall_api = (
            "https://chat-go.jwzhd.com/open-apis/v1/bot/recall?token=" + self.yhToken
        )
        self.history_api = (
            "https://chat-go.jwzhd.com/open-apis/v1/bot/messages?token=" + self.yhToken
        )

    def Recall(self, msgId: str, recvId: str, recvType: str) -> dict[str, any]:
        return self.NetJsonPost(
            self.recall_api,
            {"msgId": msgId, "chatId": recvId, "chatType": recvType},
        )

    def HistoryBefore(
        self, chatId: str, chatType: str, before: int, msgId: str = None
    ) -> dict[str, any]:
        api = (
            f"{self.history_api}&chat-id={chatId}&chat-type={chatType}&before={before}"
        )
        if msgId is not None:
            api += f"&message-id={msgId}"
        return self.NetJsonGet(api)

    def HistoryAfter(
        self, chatId: str, chatType: str, msgId: str, after: int, before: int = None
    ) -> dict[str, any]:
        api = f"{self.history_api}&chat-id={chatId}&chat-type={chatType}&message-id={msgId}&after={after}"
        if before is not None:
            api += f"&before={before}"
        return self.NetJsonGet(api)
