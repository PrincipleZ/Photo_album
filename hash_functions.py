import sha
SALT = "HUIODH*&*92asdji+_/?sdji3s9"


def hash_password(password):
    pw = SALT + password
    return sha.new(pw).hexdigest()


def hash_identifier(user_id, hashed_password):
    identifier = user_id + hashed_password
    return sha.new(identifier).hexdigest()
