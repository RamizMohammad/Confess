from fastapi import FastAPI, Request, BackgroundTasks, Query
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .Databaseconfig import ConfessServer
from .Model import *
from .Awake import keep_alive
from .Validator import ApiValidator
from .emailUtils import EmailManager
from pathlib import Path
from uuid import uuid4
import datetime

app = FastAPI()
server = ConfessServer()
validate = ApiValidator()
emailServer = EmailManager()

#* Directory setup
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

#! ----------- RESET PASSWORD ROUTES -----------

#* Primary HTML page (JS handles the token)
@app.get('/reset-password', response_class=HTMLResponse)
async def show_reset_form(request: Request, token: str = Query(default=None)):
    return templates.TemplateResponse("reset.html", {"request": request})

#* Redirect route: /reset-password/{token} → /reset-password?token=...
@app.get('/reset-password/{token}', response_class=HTMLResponse)
async def redirect_to_query_param(request: Request, token: str):
    return RedirectResponse(url=f"/reset-password?token={token}")

#* Token validation endpoint used by JS
@app.get('/validate-token/{token}')
async def validate_token(token: str):
    valid, msg = server.validateResetLink(token)
    return {"valid": valid, "message": msg if not valid else "Token is valid"}

#* Reset password endpoint called by JS
@app.post('/reset-password')
async def resetPassword(data: passwordResetModel):
    valid, result = server.validateResetLink(data.token)
    if not valid:
        return JSONResponse(status_code=400, content={"message": result})

    server.markTokenUsed(data.token)
    if server.updateUserPassword(result, data.newPassword):
        return {"message": "Password reset successful"}
    else:
        return JSONResponse(status_code=500, content={"message": "Failed to update password"})

#! ----------- USER MANAGEMENT ROUTES -----------

#* Route to create a new user
@app.post('/add-user')
async def addUser(data: addUserData, request: Request):
    if not validate.validate(request.headers.get("x-api-key")):
        return {
            "message": False
        }
    alias = server.checkExistingAlaisName(data.aliasName)
    if(alias):
        return{
            "isAliasName": alias,
            "isUserCreated": False
        }
    else:
        result = server.createUser(data.model_dump(exclude_none=True))
        return {
            "isAliasName": False,
            "isUserCreated": result
        }

#* Route to check if the user availabel or not
@app.post('/check-user')
async def checkExistingUser(data: checkUserEmail, request: Request):
    if not validate.validate(request.headers.get("x-api-key")):
        return {
            "message": False
        }
    result = server.checkUser(data.email)
    return {"message": result}

#* Route to delete the user
@app.post('/delete-user')
async def deleteTheUser(data: deleteExistingUser, request: Request):
    if not validate.validate(request.headers.get("x-api-key")):
        return {
            "message": False
        }
    result = server.deleteExistingUser(data.email)
    return {"message": result}

#* Route to check if user available and pass enabled or not
@app.post('/check-userpass')
def checkUserAndPassword(data: checkUserAndPasswordModel, request: Request):
    if not validate.validate(request.headers.get("x-api-key")):
        return {
            "message": False
        }
    isUser, isPassword = server.checkUserAndPassword(data.email)
    return{
        "isUser": isUser,
        "isPassword": isPassword
    }

#* Route to check the correct password
@app.post('/check-password')
def checkPassword(data: checkPassword, request: Request):
    if not validate.validate(request.headers.get("x-api-key")):
        return {
            "message": False
        }
    status = server.checkForCorrectPassword(
        data.email,
        data.password
    )
    return{
        "message": status
    }
#! ----------- PASSWORD RESET REQUEST FLOW -----------

#* Route to forgot the password
@app.post('/forgot-password')
async def requestUserPasswordReset(data: requestResetModel, request: Request):
    if not validate.validate(request.headers.get("x-api-key")):
        return { "message": False }

    if not server.checkUser(data.email):
        return JSONResponse(status_code=404, content={"success": False})

    token = server.passwordReset(data.email)
    if token:
        reset_link = f"https://confess-ysj8.onrender.com/reset-password/{token}"
        server.send_telegram_log(f"[Password Reset Link Generated]\nEmail: {data.email}\nLink: {reset_link}")

        # Email sending
        success = emailServer.send(
            to=data.email,
            subject="Reset Your Password",
            templateName="forgot.html",  # in /templates
            context={
                "name": data.email.split('@')[0].capitalize(),
                "reset_link": reset_link
            }
        )

        if success:
            return {"message": True}
        else:
            return {"message": False, "error": "Email failed to send"}

    return {"message": False, "error": "Token generation failed"}

#! ------------ Create Post -------------------------

#* Route to create the post
@app.post('/create-post')
async def addPost(data: postsDataModel, request: Request):
    if not validate.validate(request.headers.get("x-api-key")):
        return {
            "message": False
        }
    postData = {
        "postId": str(uuid4()),
        "email": data.email,
        "date": datetime.datetime.utcnow().isoformat(),
        "post": data.post
    }
    if server.addPost(postData):
        return{
            "message": True
        }
    else:
        return{
            "message": False
        }

#! ----------- SYSTEM STATUS + KEEP ALIVE -----------

#* Home Route
@app.get('/')
async def homeRoute():
    return {"message": server.status}

#* Awake Route
@app.get('/jagte-raho')
async def serverInvoker():
    return JSONResponse(status_code=200, content={
        "message": "Abhi Hum Jinda Hai"
    })

#! ----------- BACKGROUND TASK (keep_alive thread) -----------

@app.on_event("startup")
def start_keep_alive():
    import threading
    threading.Thread(target=keep_alive, daemon=True).start()
