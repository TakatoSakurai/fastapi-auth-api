from fastapi import FastAPI, HTTPException, Header, status
from pydantic import BaseModel, constr
from typing import Optional, Dict
from fastapi.responses import JSONResponse
from base64 import b64decode

app = FastAPI()

# 簡易的なインメモリDB
users_db: Dict[str, dict] = {}

# POST /signup 用のリクエストモデル
class SignupRequest(BaseModel):
    user_id: constr(min_length=6, max_length=20, pattern=r'^[a-zA-Z0-9]+$')
    password: constr(min_length=8, max_length=20, pattern=r'^[\x21-\x7e]+$')  # 半角英数字記号

class UpdateRequest(BaseModel):
    nickname: Optional[constr(max_length=30)] = None
    comment: Optional[constr(max_length=100)] = None

@app.post("/signup")
def signup(request: SignupRequest):
    if not request.user_id or not request.password:
        raise HTTPException(status_code=400, detail={
            "message": "Account creation failed",
            "cause": "user_id and password are required"
        })

    if request.user_id in users_db:
        raise HTTPException(status_code=400, detail={
            "message": "Account creation failed",
            "cause": "Already same user_id is used"
        })

    users_db[request.user_id] = {
        "password": request.password,
        "nickname": request.user_id,
        "comment": ""
    }

    return {
        "message": "Account successfully created",
        "user": {
            "user_id": request.user_id,
            "nickname": request.user_id
        }
    }

def authenticate(auth_header: str):
    if not auth_header or not auth_header.startswith("Basic "):
        raise HTTPException(status_code=401, detail={"message": "Authentication failed"})

    try:
        decoded = b64decode(auth_header[6:]).decode("utf-8")
        user_id, password = decoded.split(":", 1)
    except Exception:
        raise HTTPException(status_code=401, detail={"message": "Authentication failed"})

    user = users_db.get(user_id)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail={"message": "Authentication failed"})

    return user_id

@app.get("/users/{user_id}")
def get_user(user_id: str, authorization: str = Header(None)):
    auth_user_id = authenticate(authorization)

    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail={"message": "No user found"})

    return {
        "message": "User details by user_id",
        "user": {
            "user_id": user_id,
            "nickname": user.get("nickname", user_id),
            "comment": user.get("comment", "")
        }
    }

@app.patch("/users/{user_id}")
def update_user(user_id: str, request: UpdateRequest, authorization: str = Header(None)):
    auth_user_id = authenticate(authorization)

    if auth_user_id != user_id:
        raise HTTPException(status_code=403, detail={"message": "No permission for update"})

    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail={"message": "No user found"})

    if request.nickname is None and request.comment is None:
        raise HTTPException(status_code=400, detail={
            "message": "User updation failed",
            "cause": "Required nickname or comment"
        })

    if request.nickname is not None:
        if not (0 < len(request.nickname) <= 30):
            raise HTTPException(status_code=400, detail={
                "message": "User updation failed",
                "cause": "Invalid nickname or comment"
            })
        user["nickname"] = request.nickname

    if request.comment is not None:
        if not (0 <= len(request.comment) <= 100):
            raise HTTPException(status_code=400, detail={
                "message": "User updation failed",
                "cause": "Invalid nickname or comment"
            })
        user["comment"] = request.comment

    return {
        "message": "User successfully updated",
        "user": {
            "nickname": user["nickname"],
            "comment": user["comment"]
        }
    }

@app.post("/close")
def close_account(authorization: str = Header(None)):
    user_id = authenticate(authorization)
    users_db.pop(user_id, None)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Account and user successfully removed"})
