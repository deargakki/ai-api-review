from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..models.user import User, UserCreate, UserLogin, Token, TokenData

# 配置
SECRET_KEY = "your-secret-key-here"  # 在生产环境中应该使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 模拟用户数据库
fake_users_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("admin123"),
        "is_active": True,
    }
}

class AuthService:
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """获取密码哈希值"""
        return pwd_context.hash(password)

    def get_user(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        if username in fake_users_db:
            user_dict = fake_users_db[username]
            return User(**user_dict)
        return None

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户并返回用户对象"""
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, fake_users_db[username]["hashed_password"]):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def register_user(self, user_create: UserCreate) -> User:
        """注册新用户"""
        # 检查用户名是否已存在
        if user_create.username in fake_users_db:
            raise ValueError("Username already registered")

        # 创建新用户
        hashed_password = self.get_password_hash(user_create.password)
        new_user = {
            "id": len(fake_users_db) + 1,
            "username": user_create.username,
            "email": user_create.email,
            "hashed_password": hashed_password,
            "is_active": True,
        }

        # 添加到数据库
        fake_users_db[user_create.username] = new_user

        return User(**new_user)

    def decode_token(self, token: str) -> Optional[TokenData]:
        """解码令牌"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            token_data = TokenData(username=username)
        except JWTError:
            return None
        return token_data