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

    # 获取群ID【xxx】中消息 ID【xxxx】后 10 条消息，共返回 11 条消息
    # https://chat-go.jwzhd.com/open-apis/v1/bot/messages?token=xxxxx&chat-id=xxx&chat-type=group&message-id=xxxx&after=10

    # 获取群ID【xxx】中消息 ID【xxxx】前后各 10 条消息，共返回 21 条消息
    # https://chat-go.jwzhd.com/open-apis/v1/bot/messages?token=xxxxx&chat-id=xxx&chat-type=group&message-id=xxxx&before=10&after=10
