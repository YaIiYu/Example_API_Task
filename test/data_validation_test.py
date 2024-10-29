import pydantic_core
import logging
from middleware.data_validator import *

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

if __name__ == "__main__":
    try:
        user = UserV(name="15", email="bababaa@gmail.com", password="12345")
        logging.info(f"{type(user)}'s data: {user} ")

    except pydantic_core.ValidationError as ex:
        logging.error("Validation error - " + ex.__str__().replace(
            "For further information visit https://errors.pydantic.dev/2.9/v/string_type", ""))
