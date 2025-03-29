from core.database import db_instance
from typing import Optional

class Auth:
    def __init__(self):
        self.current_user: Optional[str] = None

    def register(self, username: str, password: str) -> bool:
        if db_instance.read(f"usuarios/{username}"):
            return False
        db_instance.write(f"usuarios/{username}", {"username": username, "password": password})
        return True

    def login(self, username: str, password: str) -> bool:
        user_data = db_instance.read(f"usuarios/{username}")
        if user_data and user_data.get("password") == password:
            self.current_user = username
            return True
        return False

    def logout(self) -> None:
        self.current_user = None

    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def get_current_user(self) -> Optional[str]:
        return self.current_user

auth = Auth()