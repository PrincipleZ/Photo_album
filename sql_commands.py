import hash_functions


def check_user_exist(email):
    return "SELECT * FROM User WHERE email='{}'".format(email)


def create_user(username, email, password):

    return "INSERT INTO User (name, email, password) VALUES ('{}', '{}', _binary'{}')".format(
        username, email, hash_functions.hash_password(password))


def get_user_id(email=None, username=None):
    if email:
        return "SELECT user_id FROM User WHERE email='{}'".format(email)
    elif username:
        return "SELECT user_id FROM User WHERE name='{}'".format(username)

    return ""


def get_user_info(email):

    return "SELECT hash_password, name, user_id FROM User WHERE email='{}'".format(
        email)


def create_album(albumName, description, user_id):
    return "INSERT INTO Album (name, description, user_id) VALUES ('{}', '{}', '{}')".format(
        albumName, description, user_id)


def get_albums(user_id):
    return "SELECT album_id, name FROM Album WHERE user_id = {}".format(
        user_id)
