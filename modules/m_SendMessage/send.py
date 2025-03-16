class SendMessage:
    def __init__(self, sdk):
        self.apiUrl = (
            "https://chat-go.jwzhd.com/open-apis/v1/bot/send?token="
            + sdk.MessageBase.yhToken
        )
        self.NetJsonPost = sdk.MessageBase.NetJsonPost
        self.NetFileUpload = sdk.MessageBase.NetFileUpload

    def _gen_body(
        self,
        recvId: str,
        recvType: str,
        contentType: str,
        content: dict[str, any],
        parentId: str,
    ) -> dict[str, any]:
        return {
            "recvId": recvId,
            "recvType": recvType,
            "contentType": contentType,
            "content": content,
            "parentId": parentId,
        }
