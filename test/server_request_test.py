import requests
import logging


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


data_to_send = {
    "user_id": 1,
    "content": "asdasfasdfsad",
}
response = requests.get("http://localhost:7985/posts/")
logging.info(response.json())