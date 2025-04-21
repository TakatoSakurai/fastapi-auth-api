from fastapi import FastAPI, HTTPException, Header, status
from pydantic import BaseModel, constr
from typing import Optional, Dict
from fastapi.responses import JSONResponse
from base64 import b64decode

app = FastAPI()

users_db: Dict[str, dict] = {}

class SignupRequest(BaseModel):
    user_id: constr(min_length=6, max_length=20, pattern=r'^[a-zA-Z0-9]+$')
    password: constr(min_length=8, max_length=20, pattern=r'^[ -~]+$')

class UpdateRequest(BaseModel):
    nickname: Optional[constr(max_length=30)] = None
    comment: Optional[constr(max_length=100)] = None

@app.post("/signup")
def signup(request: SignupRequest):
    if request.user_id in users_db:
        raise HTTPException(status_code=400, detail="Already same user_id is used")

    users_db[request.user_id] = {
        "password": request.password,
        "nickname": request.user_id,
        "comment": ""
    }

    return {"message": "Account successfully created",
            "user": {"user_id": request.user_id, "nickname": request.user_id}}

def authenticate(auth_header: str):
    if not auth_header or not auth_header.startswith("Basic "):
        raise HTTPException(status_code=401, detail="Authentication failed")

    decoded = b64decode(auth_header[6:]).decode("utf-8")
    user_id, password = decoded.split(":", 1)

    user = users_db.get(user_id)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Authentication failed")

    return user_id

@app.get("/users/{user_id}")
def get_user(user_id: str, authorization: str = Header(None)):
    auth_user_id = authenticate(authorization)

    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="No user found")

    user = users_db[user_id]
    return {"message": "User details by user_id",
            "user": {"user_id": user_id, "nickname": user["nickname"], "comment": user["comment"]}}

@app.patch("/users/{user_id}")
def update_user(user_id: str, request: UpdateRequest, authorization: str = Header(None)):
    auth_user_id = authenticate(authorization)

    if auth_user_id != user_id:
        raise HTTPException(status_code=403, detail="No permission for update")

    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="No user found")

    if request.nickname is None and request.comment is None:
        raise HTTPException(status_code=400, detail="Required nickname or comment")

    if request.nickname is not None:
        user["nickname"] = request.nickname or user_id

    if request.comment is not None:
        user["comment"] = request.comment

    return {"message": "User successfully updated",
            "user": {"nickname": user["nickname"], "comment": user["comment"]}}

@app.post("/close")
def close_account(authorization: str = Header(None)):
    user_id = authenticate(authorization)
    users_db.pop(user_id, None)

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Account and user successfully removed"})
