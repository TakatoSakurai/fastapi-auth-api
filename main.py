from fastapi import FastAPI, HTTPException, Header, Body
from typing import Optional, Dict
import base64

app = FastAPI()

# 仮のユーザーデータベース
users_db: Dict[str, Dict] = {}

# 認証処理
def authenticate(authorization: Optional[str]) -> str:
    if not authorization or not authorization.startswith("Basic "):
        raise HTTPException(status_code=401, detail={"message": "Authentication failed"})

    try:
        encoded = authorization.split(" ")[1]
        decoded = base64.b64decode(encoded).decode()
        user_id, password = decoded.split(":", 1)
    except:
        raise HTTPException(status_code=401, detail={"message": "Authentication failed"})

    user = users_db.get(user_id)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail={"message": "Authentication failed"})

    return user_id

@app.post("/signup")
def signup(request: dict = Body(...)):
    user_id = request.get("user_id")
    password = request.get("password")

    if not user_id or not password:
        raise HTTPException(status_code=400, detail={
            "message": "Account creation failed",
            "cause": "user_id and password are required"
        })

    if not (6 <= len(user_id) <= 20) or not user_id.isalnum():
        raise HTTPException(status_code=400, detail={
            "message": "Account creation failed",
            "cause": "Invalid user_id"
        })

    if not (8 <= len(password) <= 20):
        raise HTTPException(status_code=400, detail={
            "message": "Account creation failed",
            "cause": "Invalid password"
        })

    if user_id in users_db:
        raise HTTPException(status_code=400, detail={
            "message": "Account creation failed",
            "cause": "Already same user_id is used"
        })

    users_db[user_id] = {
        "password": password,
        "nickname": user_id,
        "comment": ""
    }

    return {
        "message": "Account successfully created",
        "user": {
            "user_id": user_id,
            "nickname": user_id
        }
    }

@app.get("/users/{user_id}")
def get_user(user_id: str, authorization: Optional[str] = Header(None)):
    auth_user_id = authenticate(authorization)

    if user_id not in users_db:
        raise HTTPException(status_code=404, detail={"message": "No user found"})

    user = users_db[user_id]
    return {
        "message": "User details by user_id",
        "user": {
            "user_id": user_id,
            "nickname": user["nickname"],
            "comment": user["comment"]
        }
    }

@app.patch("/users/{user_id}")
def update_user(user_id: str, request: dict = Body(...), authorization: Optional[str] = Header(None)):
    auth_user_id = authenticate(authorization)

    if auth_user_id != user_id:
        raise HTTPException(status_code=403, detail={"message": "No permission for update"})

    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail={"message": "No user found"})

    nickname = request.get("nickname")
    comment = request.get("comment")

    if not nickname and not comment:
        raise HTTPException(status_code=400, detail={
            "message": "User updation failed",
            "cause": "Required nickname or comment"
        })

    if nickname is not None:
        if len(nickname) > 30:
            raise HTTPException(status_code=400, detail={
                "message": "User updation failed",
                "cause": "Invalid nickname or comment"
            })
        user["nickname"] = nickname

    if comment is not None:
        if len(comment) > 100:
            raise HTTPException(status_code=400, detail={
                "message": "User updation failed",
                "cause": "Invalid nickname or comment"
            })
        user["comment"] = comment

    return {
        "message": "User successfully updated",
        "user": {
            "nickname": user["nickname"],
            "comment": user["comment"]
        }
    }

@app.post("/close")
def delete_user(authorization: Optional[str] = Header(None)):
    user_id = authenticate(authorization)

    if user_id in users_db:
        del users_db[user_id]

    return {"message": "Account and user successfully removed"}
