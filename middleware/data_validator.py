import pydantic_core
from pydantic import BaseModel


class BasePattern(BaseModel):
    pass


class UserV(BasePattern):
    name: str
    email: str
    password: str
    logged: bool = False
    is_admin: bool = False


class PostsV(BasePattern):
    user_id: int
    title: str
    content: str


class CommentV(BasePattern):
    user_id: int
    post_id: int
    content: str


# Test
if __name__ == "__main__":
    try:
        user = UserV(name=15, email="bababaa@gmail.com", password="12345")
        print(type(user))

    except pydantic_core.ValidationError as ex:
        print("Validation error - ",
              ex.__str__().replace("For further information visit https://errors.pydantic.dev/2.9/v/string_type", ""))
