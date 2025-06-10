from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from Databaseconfig import ConfessServer
from Model import addUserData, checkUserEmail, deleteExistingUser, requestResetModel, passwordResetModel
from Awake import keep_alive
from pathlib import Path

app = FastAPI()
server = ConfessServer()

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get('/reset-password/{token}', response_class=HTMLResponse)
async def show_reset_form(request: Request, token: str):
    return templates.TemplateResponse("reset.html", {"request": request})

@app.get('/jagte-raho')
async def serverInvoker():
    return "Abhi Hum Jinda Hai"

@app.get('/')
async def homeRoute():
    return {"message": server.status}

@app.post('/add-user')
async def addUser(data: addUserData):
    result = server.createUser(data.model_dump(exclude_none=True))
    return {"message": result}

@app.post('/check-user')
async def checkExistingUser(data: checkUserEmail):
    result = server.checkUser(data.email)
    return {"message": result}

@app.post('/delete-user')
async def deleteTheUser(data: deleteExistingUser):
    result = server.deleteExistingUser(data.email)
    return {"message": result}

@app.post('/request-reset')
async def requestUserPasswordReset(data: requestResetModel):
    if not server.checkUser(data.email):
        return JSONResponse(status_code=404, content={"success": False})
    
    token = server.passwordReset(data.email)
    if token:
        link = f"https://confess-ysj8.onrender.com/reset-password/{token}"
        server.send_telegram_log(f"[Password Reset Link Generated]\nEmail: {data.email}\nLink: {link}")
        return {"success": True}

    return JSONResponse(status_code=500, content={"success": False})

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
    
@app.get('/validate-token/{token}')
async def validate_token(token: str):
    valid, msg = server.validateResetLink(token)
    return {"valid": valid, "message": msg if not valid else "Token is valid"}
    
@app.get('/reset-password/{token}', response_class=HTMLResponse)
async def show_reset_form(request: Request, token: str):
    valid, msg = server.validateResetLink(token)
    if not valid:
        return templates.TemplateResponse("invalid_token.html", {"request": request, "message": msg})
    return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})

@app.on_event("startup")
def start_keep_alive():
    import threading
    threading.Thread(target=keep_alive, daemon=True).start()