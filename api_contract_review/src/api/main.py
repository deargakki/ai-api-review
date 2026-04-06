from fastapi import FastAPI, HTTPException, WebSocket, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..services.flow import ReviewFlow
from ..services.auth import AuthService
from ..models.user import User, UserCreate, UserLogin, Token, TokenData
from pydantic import BaseModel
from datetime import timedelta
import json

app = FastAPI(
    title="API Contract Review API",
    description="API for reviewing API contract changes",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
review_flow = ReviewFlow()
auth_service = AuthService()

# OAuth2 密码承载令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = auth_service.decode_token(token)
    if token_data is None:
        raise credentials_exception
    user = auth_service.get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Pydantic 模型
class ReviewRequest(BaseModel):
    confluence_page_id: str
    github_repo: str
    github_file: str
    github_branch: str = "master"

class ReviewResponse(BaseModel):
    success: bool
    generated_openapi: str
    comparison_result: dict
    spectral_result: dict
    summary: dict

# 路由
@app.post("/api/review", response_model=ReviewResponse)
async def run_review(request: ReviewRequest, current_user: User = Depends(get_current_user)):
    """运行 API 变更审查流程"""
    try:
        # 运行审查
        result = review_flow.run_review(
            request.confluence_page_id,
            request.github_repo,
            request.github_file,
            request.github_branch
        )
        
        # 检查是否有错误
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return ReviewResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录"""
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/register", response_model=User)
async def register(user_create: UserCreate):
    """用户注册"""
    try:
        user = auth_service.register_user(user_create)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok"}

# WebSocket 连接管理
active_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点，用于实时发送进度更新"""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # 保持连接活跃
            await websocket.receive_text()
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)

# 发送进度更新的函数
def send_progress_update(progress, message):
    """发送进度更新到所有连接的客户端"""
    import asyncio
    async def send_message():
        for connection in active_connections:
            try:
                await connection.send_text(json.dumps({"progress": progress, "message": message}))
            except Exception as e:
                print(f"Error sending progress update: {e}")
    asyncio.run(send_message())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)