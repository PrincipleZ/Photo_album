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


def get_album_owner(album_id):
    return "SELECT user_id FROM Album WHERE album_id = {}".format(album_id)


def create_photo(album_id, name, file_path):
    return "INSERT INTO Photo (name, album_id, file_path) VALUES ('{}', {}, '{}')".format(
        name, album_id, file_path)


def get_next_photo_id():
    return "SELECT photo_id FROM Photo ORDER BY photo_id DESC LIMIT 1"


def check_photo_id(photo_id):
    return "SELECT name FROM Photo WHERE photo_id={}".format(photo_id)


def get_photo_id(path):
    return "SELECT photo_id FROM Photo WHERE file_path = '{}'".format(path)


def update_file_path(new_path, photo_id):
    return "UPDATE Photo SET file_path='{}' WHERE photo_id = {}".format(
        new_path, photo_id)


def get_photos_from_album(album_id):
    return "SELECT name, file_path FROM Photo WHERE album_id = {}".format(
        album_id)


def get_thumbnail(album_id):
    return "SELECT file_path FROM Photo WHERE album_id = {} LIMIT 1".format(
        album_id)


def count_photo_from_album(album_id):
    return "SELECT COUNT(*) From Photo WHERE album_id = {}".format(album_id)


def get_album_name(album_id):
    return "SELECT name FROM Album WHERE album_id = {}".format(album_id)
