class Board:
    def __init__(self, sdk, logger):
        self.yhToken = sdk.MessageBase.yhToken
        self.NetJsonPost = sdk.MessageBase.NetJsonPost
        self.local_board_api = (
            "https://chat-go.jwzhd.com/open-apis/v1/bot/board?token=" + self.yhToken
        )
        self.global_board_api = (
            "https://chat-go.jwzhd.com/open-apis/v1/bot/board-all?token=" + self.yhToken
        )

    def _gen_local_body(
        self,
        chatId: str,
        chatType: str,
        contentType: str,
        content: str,
        memberId: str,
        expireTime: int,
    ) -> dict[str, str]:
        return {
            "chatId": chatId,
            "chatType": chatType,
            "contentType": contentType,
            "content": content,
            "memberId": memberId,
            "expireTime": expireTime,
        }

    def _gen_global_body(
        self, contentType: str, content: str, expireTime: int
    ) -> dict[str, str]:
        return {
            "contentType": contentType,
            "content": content,
            "expireTime": expireTime,
        }

    def LocalText(
        self,
        chatId: str,
        chatType: str,
        content: str,
        memberId: str = "",
        expireTime: int = 0,
    ) -> dict[str, any]:
        return self.NetJsonPost(
            self.local_board_api,
            self._gen_local_body(
                chatId, chatType, "text", content, memberId, expireTime
            ),
        )

    def LocalMarkdown(
        self,
        chatId: str,
        chatType: str,
        content: str,
        memberId: str = "",
        expireTime: int = 0,
    ) -> dict[str, any]:
        return self.NetJsonPost(
            self.local_board_api,
            self._gen_local_body(
                chatId, chatType, "markdown", content, memberId, expireTime
            ),
        )

    def LocalHtml(
        self,
        chatId: str,
        chatType: str,
        content: str,
        memberId: str = "",
        expireTime: int = 0,
    ) -> dict[str, any]:
        return self.NetJsonPost(
            self.local_board_api,
            self._gen_local_body(
                chatId, chatType, "html", content, memberId, expireTime
            ),
        )

    def LocalDismiss(
        self, chatId: str, chatType: str, memberId: str = ""
    ) -> dict[str, any]:
        return self.NetJsonPost(
            "https://chat-go.jwzhd.com/open-apis/v1/bot/board-dismiss?token="
            + self.yhToken,
            {"chatId": chatId, "chatType": chatType, "memberId": memberId},
        )

    def GlobalText(self, content: str, expireTime: int = 0) -> dict[str, any]:
        return self.NetJsonPost(
            self.global_board_api, self._gen_global_body("text", content, expireTime)
        )

    def GlobalMarkdown(self, content: str, expireTime: int = 0) -> dict[str, any]:
        return self.NetJsonPost(
            self.global_board_api,
            self._gen_global_body("markdown", content, expireTime),
        )

    def GlobalHtml(self, content: str, expireTime: int = 0) -> dict[str, any]:
        return self.NetJsonPost(
            self.global_board_api, self._gen_global_body("html", content, expireTime)
        )

    def GlobalDismiss(self) -> dict[str, any]:
        return self.NetJsonPost(
            "https://chat-go.jwzhd.com/open-apis/v1/bot/board-all-dismiss?token="
            + self.yhToken,
            {},
        )
