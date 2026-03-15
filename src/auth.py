"""
用户认证模型 - 汽配云助手

使用SQLAlchemy存储用户数据
支持密码哈希和JWT令牌
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

Base = declarative_base()


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)

    # 用户信息
    full_name = Column(String(100))
    role = Column(String(20), default="user")  # admin, user, readonly

    # 状态
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # API令牌
    api_token = Column(String(64), unique=True, index=True)
    token_expires = Column(DateTime)

    def set_password(self, password: str):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def generate_api_token(self, expires_hours: int = 24):
        """生成API令牌"""
        self.api_token = secrets.token_hex(32)
        self.token_expires = datetime.utcnow() + timedelta(hours=expires_hours)
        return self.api_token

    def is_token_valid(self) -> bool:
        """检查令牌是否有效"""
        if not self.api_token or not self.token_expires:
            return False
        return datetime.utcnow() < self.token_expires

    def to_dict(self, include敏感信息: bool = False):
        """转换为字典"""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

        if include敏感信息:
            data["api_token"] = self.api_token
            data["token_expires"] = (
                self.token_expires.isoformat() if self.token_expires else None
            )

        return data

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


class AuthManager:
    """认证管理器"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            project_root = Path(__file__).parent.parent
            db_path = project_root / "data" / "qipeiyun.db"

        self.db_path = db_path
        self.engine = None
        self.Session = None

    def init_db(self):
        """初始化数据库"""
        from sqlalchemy import create_engine

        # 确保数据库目录存在
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        return self

    def get_session(self):
        """获取数据库会话"""
        if self.Session is None:
            self.init_db()
        return self.Session()

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str = None,
        role: str = "user",
    ) -> User:
        """创建新用户"""
        session = self.get_session()

        try:
            # 检查用户名和邮箱是否已存在
            existing = (
                session.query(User)
                .filter((User.username == username) | (User.email == email))
                .first()
            )

            if existing:
                if existing.username == username:
                    raise ValueError(f"用户名 {username} 已存在")
                else:
                    raise ValueError(f"邮箱 {email} 已存在")

            # 创建用户
            user = User(
                username=username,
                email=email,
                full_name=full_name or username,
                role=role,
            )
            user.set_password(password)

            session.add(user)
            session.commit()

            return user

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def authenticate(self, username: str, password: str) -> User:
        """验证用户登录"""
        session = self.get_session()

        try:
            user = (
                session.query(User)
                .filter((User.username == username) | (User.email == username))
                .first()
            )

            if not user:
                raise ValueError("用户不存在")

            if not user.is_active:
                raise ValueError("账户已被禁用")

            if not user.check_password(password):
                raise ValueError("密码错误")

            # 更新最后登录时间
            user.last_login = datetime.utcnow()
            session.commit()

            # 返回用户数据副本，避免detached问题
            user_data = user.to_dict()

            return user_data

        finally:
            session.close()

    def get_user_by_id(self, user_id: int) -> User:
        """根据ID获取用户"""
        session = self.get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()

    def get_user_by_username(self, username: str) -> User:
        """根据用户名获取用户"""
        session = self.get_session()
        try:
            return session.query(User).filter(User.username == username).first()
        finally:
            session.close()

    def verify_token(self, token: str) -> User:
        """验证API令牌"""
        session = self.get_session()

        try:
            user = session.query(User).filter(User.api_token == token).first()

            if not user:
                return None

            if not user.is_active:
                return None

            if not user.is_token_valid():
                return None

            return user

        finally:
            session.close()

    def create_admin_user(self, username: str = "admin", password: str = "admin123"):
        """创建管理员用户（如果不存在）"""
        session = self.get_session()

        try:
            admin = session.query(User).filter(User.username == username).first()

            if not admin:
                admin = User(
                    username=username,
                    email="admin@qipeiyun.com",
                    full_name="系统管理员",
                    role="admin",
                    is_active=True,
                    is_verified=True,
                )
                admin.set_password(password)
                session.add(admin)
                session.commit()
                print(f"✅ 管理员用户已创建: {username}")
                return admin
            else:
                print(f"ℹ️ 管理员用户已存在: {username}")
                return admin

        except Exception as e:
            session.rollback()
            print(f"❌ 创建管理员失败: {e}")
            return None
        finally:
            session.close()


# 便捷函数
def init_auth(db_path: str = None):
    """初始化认证系统"""
    auth = AuthManager(db_path)
    auth.init_db()
    return auth


def create_default_admin(db_path: str = None):
    """创建默认管理员"""
    auth = AuthManager(db_path)
    auth.init_db()
    return auth.create_admin_user()
