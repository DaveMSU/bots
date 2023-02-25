import requests
import typing as tp


SERVER_IP: str = "77.242.105.252"
SERVER_PORT: str = "8443"
SERVER_PROTOCOL: str = "http"
# FIRST_MESSAGE_DATE: int = 943754400


class TelegramBot:
    def __init__(self, token: str):
        self._token: str = token
        self._protocol: str = SERVER_PROTOCOL
        self._server_ip: str = SERVER_IP
        self._server_port: str = SERVER_PORT
        self._last_message_date: tp.Optional[int] = None

    @property
    def server_url(self):
        return f"{self._protocol}://{self._server_ip}:{self._server_port}"

    def get_me(self) -> tp.Any:
        url = f"{self.server_url}/bot{self._token}/getMe"
        response = requests.post(url)
        return response

    def send_message(
            self,
            chat_id: int,
            text: str
        ) -> tp.Any:
        """
        :param  chat_id: unique id of chat with bot in telegram for specifing the dialog.
        :param text: text of message that to be wanted to send to user from bot.
        :return: Nothing is return by this function.
        """
        url = f"{self.server_url}/bot{self._token}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        response = requests.post(url, data=data)
        return response

    def look_for_new_message(self) -> tp.Optional[tp.Dict[str, tp.Any]]:
        url = f"{self.server_url}/bot{self._token}/getUpdates"
        response = requests.post(url, data={"limit": 10, "offset": -1})
        all_messages = response.json()["result"]
        assert isinstance(all_messages, list), str(type(all_messages))  # TODO: remove.

        if all_messages:
            last_message = all_messages[-1]
            date_of_message = last_message["message"]["date"]  # timestamp.
            assert (self._last_message_date is None) or \
                   (self._last_message_date <= date_of_message)

            if self._last_message_date is None:
                self._last_message_date = date_of_message

            elif date_of_message > self._last_message_date:  # new message appeared.
                self._last_message_date = date_of_message
                return last_message

