from base64 import b64encode, b64decode
from hashlib import sha512
from passlib.hash import argon2

"""
    Password Hashing

    A random salt is used inside the argon2.using(rounds=4).hash(sha_hash.digest()) function

"""

def hash_password(password):
    sha_hash = sha512(password.encode("utf-8"))
    argon2_hash = argon2.using(rounds=3).hash(sha_hash.digest())
    argon2_hash = argon2_hash.encode()  # turns string to 'bytes like object'
    return b64encode(argon2_hash)


def check_password(password, hash_):
    argon2_hash = b64decode(hash_)
    argon2_hash = argon2_hash.decode()  # turns 'bytes like object' to string
    sha_hash = sha512(password.encode("utf-8"))
    return argon2.verify(sha_hash.digest(), argon2_hash)
