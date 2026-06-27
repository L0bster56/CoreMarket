from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptHasher:
    def hash(self, password: str) -> str:
        return _pwd_context.hash(password)

    def verify(self, password: str, hashed_password: str) -> bool:
        return _pwd_context.verify(password, hashed_password)
