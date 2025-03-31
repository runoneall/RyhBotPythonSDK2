class EditMessage:
    def __init__(self, sdk, logger):
        self.yhToken = sdk.MessageBase.yhToken
        self.apiUrl = (
            "https://chat-go.jwzhd.com/open-apis/v1/bot/edit?token=" + self.yhToken
        )
        self.NetJsonPost = sdk.MessageBase.NetJsonPost

    def _gen_body(
        self,
        msgId: str,
        recvId: str,
        recvType: str,
        contentType: str,
        content: dict[str, any],
    ) -> dict[str, any]:
        return {
            "msgId": msgId,
            "recvId": recvId,
            "recvType": recvType,
            "contentType": contentType,
            "content": content,
        }

    def Text(
        self,
        msgId: str,
        recvId: str,
        recvType: str,
        content: str,
        buttons: list[list[dict[str, any]]] = [],
    ) -> dict[str, any]:
        return self.NetJsonPost(
            self.apiUrl,
            self._gen_body(
                msgId,
                recvId,
                recvType,
                "text",
                {"text": content, "buttons": buttons},
            ),
        )

    def Markdown(
        self,
        msgId: str,
        recvId: str,
        recvType: str,
        content: str,
        buttons: list[list[dict[str, any]]] = [],
    ) -> dict[str, any]:
        return self.NetJsonPost(
            self.apiUrl,
            self._gen_body(
                msgId,
                recvId,
                recvType,
                "markdown",
                {"text": content, "buttons": buttons},
            ),
        )
