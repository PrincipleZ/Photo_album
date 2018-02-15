import hash_functions


check_user_exist = "SELECT * FROM User WHERE email=%s"


create_user = "INSERT INTO User (name, email, hash_password) VALUES (%s, %s, %s)"


get_user_id_with_email = "SELECT user_id FROM User WHERE email=%s"
get_user_id_with_username = "SELECT user_id FROM User WHERE name=%s"
get_user_info = "SELECT hash_password, name, user_id FROM User WHERE email=%s"


create_album = "INSERT INTO Album (name, description, user_id) VALUES (%s, %s, %s)"


get_albums = "SELECT album_id, name FROM Album WHERE user_id = %s"


get_album_owner = "SELECT user_id FROM Album WHERE album_id = %s"


create_photo = "INSERT INTO Photo (name, album_id, file_path) VALUES (%s, %s, %s)"


get_next_photo_id = "SELECT photo_id FROM Photo ORDER BY photo_id DESC LIMIT 1"


check_photo_id = "SELECT name FROM Photo WHERE photo_id= %s"


get_photo_id = "SELECT photo_id FROM Photo WHERE file_path = %s"


update_file_path = "UPDATE Photo SET file_path=%s WHERE photo_id = %s"


get_photos_from_album = "SELECT name, file_path FROM Photo WHERE album_id = %s"


get_thumbnail = "SELECT file_path FROM Photo WHERE album_id = %s LIMIT 1"


count_photo_from_album = "SELECT COUNT(*) From Photo WHERE album_id = %s"


get_album_name_and_desc = "SELECT name, description FROM Album WHERE album_id = %s"

delete_album = "DELETE FROM Album WHERE album_id = %s"
