from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from pwdlib.hashers.argon2 import Argon2Hasher

password_hasher = PasswordHash([Argon2Hasher(),BcryptHasher()])


def main():
    password = 'hello123'
    hashed_value1 = password_hasher.hash(password)
    
    result1 = password_hasher.verify(password,hashed_value1)
   
    print(hashed_value1)
    print(result1)
   

if __name__=='__main__':
    main()


def hash(password : str):
    return password_hasher.hash(password)


def VerifyHash(password:str,hashedPass:str):
    return password_hasher.verify(password,hashedPass)

