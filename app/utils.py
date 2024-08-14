from argon2 import PasswordHasher, exceptions

pwd_context = PasswordHasher()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     try:
#         return pwd_context.verify(hashed_password, plain_password)
#     except exceptions.InvalidHashError:
#         return False


def verify_password(plain_password: str, hashed_password: str) -> bool:
    print(f"Verifying password: {plain_password}")
    print(f"With hashed password: {hashed_password}")
    try:
        return pwd_context.verify(hashed_password, plain_password)
    except exceptions.InvalidHashError:
        print("Invalid hash error")
        return False
