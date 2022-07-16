import typing as tp

from global_vars import LOGGER


def parse_and_log(request_json: tp.Dict[str, tp.Any]) -> None:
    """
    Parsing dict, construct log line and pass it to logger.

    :param request_json: data of POST request passed to bot.
    """
    chat_id = request_json["message"]["chat"]["id"]
    message_text = request_json["message"]["text"]
    
    addressee = request_json["message"]["from"]
    user_name = addressee.get("username")
    real_name = " ".join(
        [
            str(addressee.get("first_name")), 
            str(addressee.get("last_name"))
        ]
    )
    
    log_line = f"chat_id={chat_id}. "\
               f"username={user_name}. "\
               f"real_name={real_name}. "\
               f"message=\"{message_text}\""
    
    LOGGER.debug(log_line) 

