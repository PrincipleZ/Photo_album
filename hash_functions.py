import sha


def hash_password(password):
    return sha.new(password).hexdigest()
