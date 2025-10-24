import hashlib, os

def hash_password(password):
    """
    Hash a given password
    """
    
    salt = os.urandom(16)

    hashed_password = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000 
    )

    return (salt + hashed_password).hex()


def verify_password(password, stored_password):
    """
    Confirm if an entered password is the same as a hashed password
    """

    stored_password_bytes = bytes.fromhex(stored_password)
    salt = stored_password_bytes[:16]
    stored_hash = stored_password_bytes[16:]
    new_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )

    return new_hash == stored_hash