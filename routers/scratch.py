from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "123456"

hashed_password = bcrypt_context.hash(password)

print(bcrypt_context.verify(password, hashed_password))
