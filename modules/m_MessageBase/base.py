import requests


class MessageBase:
    def __init__(self, sdk) -> None:
        self.yhToken = ""

    def setToken(self, token) -> None:
        self.yhToken = token

    def NetGet(self, url) -> dict[str, any]:
        return requests.get(url=url).json()

    def NetJsonPost(self, url, data) -> dict[str, any]:
        return requests.post(
            url=url, headers={"Content-Type": "application/json"}, json=data
        ).json()

    def NetFileUpload(self, url, name, file: bytes) -> dict[str, any]:
        return requests.post(
            url=url,
            headers={"Content-Type": "multipart/form-data"},
            files=[(name, file)],
        ).json()
