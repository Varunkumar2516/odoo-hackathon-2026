from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from pwdlib.hashers.argon2 import Argon2Hasher
from datetime import datetime,timezone
password_hasher = PasswordHash([Argon2Hasher(),BcryptHasher()])


def main():
    password = 'm416'
    hashed_value1 = password_hasher.hash(password)
    
    result1 = password_hasher.verify(password,hashed_value1)
   
    print(hashed_value1)
    print(result1)

    print(datetime.now(timezone.utc))
   
main()