import urllib
from typing import Any
import crud
from fastapi import FastAPI, Depends, Request
import logging

logging.basicConfig(filename='errors.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(levelname)s [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.ERROR)

logger = logging.getLogger(__name__)
app = FastAPI()


async def get_body(request: Request):
    return await request.body()


@app.post("/client")
def input_request(body: Any = Depends(get_body)):
    result = urllib.parse.parse_qs(str(body), keep_blank_values=False, strict_parsing=False, encoding='utf-8',
                                   errors='replace', max_num_fields=None)

    phone = result.get("object[custom_user_id]")
    text = result.get("object[content]")
    attachments = result.get("object[attachments][0][url]")
    try:
        if text and attachments:
            crud.send_message(phone[0], text[0])
            crud.send_message(phone[0], attachments[0])
            crud.send_client_to_db(phone[0])
        elif text:
            crud.send_message(phone[0], text[0])
            crud.send_client_to_db(phone[0])
        elif attachments:
            crud.send_message(phone[0], attachments[0])
            crud.send_client_to_db(phone[0])
        return result
    except:
        logger.error("Ошибка отправки оператором сообщения из Omnidesk")


# if __name__ == '__main__':
#     uvicorn.run(app)
