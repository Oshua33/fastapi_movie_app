from argon2 import PasswordHasher, exceptions

# Initialize the Argon2 password hasher
ph = PasswordHasher()

password = "mysecretpassword"

# Hash the password
hashed_password = ph.hash(password)
print("Hashed Password:", hashed_password)

# Verify the password
try:
    is_correct = ph.verify(hashed_password, password)
    print("Password match:", is_correct)
except exceptions.InvalidHashError:
    print("Invalid hash error")
