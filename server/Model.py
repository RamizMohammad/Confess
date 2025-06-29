from pydantic import BaseModel, model_validator
from typing import Optional
from .Databaseconfig import ConfessServer

server = ConfessServer()

class addUserData(BaseModel):
    email: str
    aliasName: str
    about: str
    date: str
    isPassword: bool
    password: Optional[str] = None

    @model_validator(mode='after')
    def passwordValidator(self) -> 'addUserData':
        if self.isPassword and not self.password:
            server.send_telegram_log("There is error in setting the password")
            raise ValueError("Password must be provided if isPassword is True")
        return self

class checkUserEmail(BaseModel):
    email: str

class deleteExistingUser(BaseModel):
    email: str

class requestResetModel(BaseModel):
    email: str

class passwordResetModel(BaseModel):
    token: str
    newPassword: str

class checkUserAndPasswordModel(BaseModel):
    email: str

class checkPassword(BaseModel):
    email: str
    password: str

class postsDataModel(BaseModel):
    email: str
    post: str

class postStatusModel(BaseModel):
    postId: str
    likeCount: int
    supportCount: int
    usBhaiCount: int