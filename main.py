#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import MySQLdb
import jinja2
import sql_commands
import hash_functions
import cloudstorage as gcs
from google.appengine.api import app_identity
import logging
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import sys

if sys.version_info.major < 3:
    reload(sys)
sys.setdefaultencoding('utf8')

CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')
BUCKET_NAME = "yuanze-photos"

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.dirname(__file__)))


def connect_to_cloudsql():
    # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
    # will be set to 'Google App Engine/version'.
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at
        # /cloudsql/cloudsql-connection-name.
        cloudsql_unix_socket = os.path.join(
            '/cloudsql', CLOUDSQL_CONNECTION_NAME)
        logging.info("Connected to online database")
        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            passwd=CLOUDSQL_PASSWORD, use_unicode=True, charset="utf8")

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        db = MySQLdb.connect(
            host='127.0.0.1',
            user=CLOUDSQL_USER,
            passwd=CLOUDSQL_PASSWORD,
            use_unicode=True,
            charset="utf8")
        logging.info("Connected to local database")

    return db


class MainPage(webapp2.RequestHandler):

    def get(self):
        """Simple request handler that shows all of the MySQL variables."""
        self.response.headers['Content-Type'] = 'text/plain'

        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute('USE main')
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS User(user_id INTEGER NOT NULL AUTO_INCREMENT, name VARCHAR(255), email VARCHAR(255), password VARCHAR(255), PRIMARY KEY(user_id)) ENGINE = InnoDB')
        cursor.execute("CREATE TABLE IF NOT EXISTS Album (album_id INTEGER NOT NULL AUTO_INCREMENT, name VARCHAR(255), description TEXT, user_id INTEGER, PRIMARY KEY(album_id), CONSTRAINT FOREIGN KEY (user_id) REFERENCES User (user_id) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE = InnoDB")
        cursor.execute("CREATE TABLE IF NOT EXISTS Photo (photo_id INTEGER NOT NULL AUTO_INCREMENT, name VARCHAR(255), upload_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, file_path VARCHAR(255), album_id INTEGER, PRIMARY KEY(photo_id), CONSTRAINT FOREIGN KEY (album_id) REFERENCES Album (album_id) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE = InnoDB")
        cursor.execute('SHOW VARIABLES')

        for r in cursor.fetchall():
            self.response.write('{}\n'.format(r))


class RegisterHandler(webapp2.RequestHandler):

    def get(self):
        self.redirect('/')

    def post(self):
        db, cursor = get_conn_and_cursor()
        email = self.request.get('email')
        pw = self.request.get('key')
        username = self.request.get('username')
        cursor.execute(sql_commands.check_user_exist, (email,))
        result = cursor.fetchone()
        if not result:
            cursor.execute(
                sql_commands.create_user,
                (username,
                 email,
                 hash_functions.hash_password(pw)))
            cursor.execute(sql_commands.get_user_id_with_email, (email,))
            db.commit()
            user_id = cursor.fetchone()[0]
            self.response.set_cookie('user_id', str(user_id), max_age=1200)
            self.response.set_cookie(
                'identifier',
                hash_functions.hash_identifier(
                    str(user_id),
                    hash_functions.hash_password(pw)),
                max_age=1200)
            close_connection(db, cursor)
            self.redirect('/fakehome', self.response)
        else:
            close_connection(db, cursor)
            self.redirect('/?exist=True')


class LoginHandler(webapp2.RequestHandler):

    def get(self):
        render_var = {"ERROR": ""}
        if self.request.get('exist'):
            render_var[
                'ERROR'] = "The email has already been registered. Please log in directly or use another email to register."
        template = JINJA_ENVIRONMENT.get_template('template/login.html')
        self.response.out.write(template.render(render_var))

    def post(self):
        db, cursor = get_conn_and_cursor()
        email = self.request.get('email')
        pw = self.request.get('key')
        cursor.execute(sql_commands.get_user_info, (email,))

        result = cursor.fetchone()
        if not result or result[0] != hash_functions.hash_password(pw):
            template = JINJA_ENVIRONMENT.get_template('template/login.html')
            close_connection(db, cursor)
            self.response.out.write(template.render(
                {"ERROR": "Invalid email/password combination, please try again."}))
        else:
            self.response.set_cookie('user_id', str(result[2]), max_age=1200)
            self.response.set_cookie(
                'identifier',
                hash_functions.hash_identifier(
                    str(result[2]),
                    result[0]),
                max_age=1200)
            close_connection(db, cursor)
            self.redirect('/fakehome', self.response)


class HomeHandler(webapp2.RequestHandler):

    def get(self):
        db, cursor = get_conn_and_cursor()
        user_id = get_user_id_from_cookie(self, cursor)
        if user_id == -1:
            return self.redirect('/')
        if not self.request.get("redirected"):
            return self.redirect('/fakehome')

        cursor.execute(sql_commands.get_albums, (user_id,))
        results = cursor.fetchall()
        result_list = []
        for i in xrange(len(results)):

            result_list.append(list(results[i]))
            temp_id = results[i][0]
            cursor.execute(sql_commands.get_thumbnail, (temp_id,))
            path = cursor.fetchone()
            photo_number = 0
            if path:
                path = path[0]
                cursor.execute(sql_commands.count_photo_from_album, (temp_id,))
                photo_number = cursor.fetchone()[0]
            else:
                path = "none"
            result_list[i].append(path)
            result_list[i].append(photo_number)
            if photo_number > 1:
                result_list[i].append("s")
            else:
                result_list[i].append("")

        render_var = {
            "LOGGEDIN": True,
            "ALBUM_NAME": "",
            "ALBUMS": result_list}
        close_connection(db, cursor)
        template = JINJA_ENVIRONMENT.get_template('template/usermain.html')
        self.response.out.write(template.render(render_var))


class LogoutHandler(webapp2.RequestHandler):

    def get(self):
        self.response.delete_cookie("user_id")
        self.response.delete_cookie("identifier")
        self.redirect('/', self.response)


class AlbumCreateHandler(webapp2.RequestHandler):

    def get(self):
        self.redirect('/fakehome')

    def post(self):
        db, cursor = get_conn_and_cursor()
        name = self.request.get('albumname')
        desc = self.request.get('description')
        user_id = get_user_id_from_cookie(self, cursor)
        if user_id == -1:
            return self.redirect('/')
        cursor.execute(sql_commands.create_album, (name, desc, user_id))
        db.commit()
        close_connection(db, cursor)
        self.redirect('/home?redirected=True')


class AlbumContentHandler(webapp2.RequestHandler):

    def get(self):
        db, cursor = get_conn_and_cursor()
        if not self.request.get("redirected"):
            return self.redirect(
                '/fakehome?from={}'.format(self.request.path))
        album_id = self.request.path[7:]
        album_id = int(album_id)
        ownership = False
        user_id = get_user_id_from_cookie(self, cursor)
        if user_id > 0:
            cursor.execute(sql_commands.get_album_owner, (album_id,))
            try:
                owner = cursor.fetchone()[0]
            except:
                self.response.out.write(
                    "The album you are trying to access does not exist.")
                return
            if owner == user_id:
                ownership = True
        cursor.execute(sql_commands.get_photos_from_album, (album_id,))
        results = cursor.fetchall()
        cursor.execute(sql_commands.get_album_name_and_desc, (album_id,))
        album_name = cursor.fetchone()

        render_var = {
            "PHOTOS": results,
            "OWNER": ownership,
            "ALBUM_NAME": album_name[0],
            "DESCRIPTION": album_name[1]}
        template = JINJA_ENVIRONMENT.get_template('template/album.html')
        print(render_var)
        close_connection(db, cursor)
        self.response.out.write(template.render(render_var))


class UploadHandler(webapp2.RequestHandler):

    def get(self):
        self.redirect('/fakehome')

    def post(self):
        db, cursor = get_conn_and_cursor()
        upload_file = self.request.POST.get('photo')
        name = self.request.get('photoname')
        if not name:
            name = upload_file.filename
        name = unicode(name)
        album_id = self.request.get('albumSelection')
        cursor.execute(sql_commands.get_next_photo_id)
        result = cursor.fetchone()
        if not result:
            next_id = 1
        else:
            next_id = result[0] + 1
        file_path = create_file_path(album_id, next_id)
        cursor.execute(
            sql_commands.create_photo, (
                name,
                album_id,
                file_path))
        db.commit()
        cursor.execute(sql_commands.check_photo_id, (next_id,))
        result = cursor.fetchone()
        try:
            result = cursor.fetchone()[0]
            if result != name:
                raise Exception
        except:
            cursor.execute(
                sql_commands.get_photo_id, (
                    file_path,))
            new_id = cursor.fetchone()[0]
            file_path = create_file_path(album_id, new_id)
            cursor.execute(
                sql_commands.update_file_path, (
                    file_path,
                    new_id))
            db.commit()

        create_file(
            upload_file.type,
            file_path,
            upload_file.value)
        close_connection(db, cursor)
        self.redirect('/album/' + str(album_id) + "?redirected=True")


def create_file(file_type, filename, data):
    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    gcs_file = gcs.open(filename,
                        'w',
                        content_type=file_type,
                        options={'x-goog-meta-foo': 'foo',
                                 'x-goog-meta-bar': 'bar'},
                        retry_params=write_retry_params)
    gcs_file.write(data)
    gcs_file.close()


class HomeWithMusic(webapp2.RequestHandler):

    def get(self):
        db, cursor = get_conn_and_cursor()
        forward_path = self.request.get('from')
        user_id = get_user_id_from_cookie(self, cursor)
        if user_id == -1:
            if forward_path:

                render_var = {"GREETING": "Welcome, my guest!",
                              "SOURCE": forward_path, "LOGGEDIN": False}
                template = JINJA_ENVIRONMENT.get_template(
                    'template/frame.html')
                self.response.headers.add("redirected", "True")
                return self.response.out.write(template.render(render_var))
            else:
                return self.redirect('/')
        if not forward_path:
            forward_path = "/home"
        cursor.execute(
            "SELECT name FROM User WHERE user_id = {}".format(user_id))
        username = cursor.fetchone()[0]
        render_var = {"GREETING": "Hi, {}!".format(username),
                      "SOURCE": forward_path, "LOGGEDIN": True}
        template = JINJA_ENVIRONMENT.get_template('template/frame.html')
        self.response.headers.add("redirected", "True")
        close_connection(db, cursor)
        self.response.out.write(template.render(render_var))


class DeleteHandler(webapp2.RequestHandler):

    def get(self):
        self.redirect('/fakehome')

    def post(self):
        db, cursor = get_conn_and_cursor()
        user_id = get_user_id_from_cookie(self, cursor)
        if user_id == -1:
            return self.redirect('/')
        target = self.request.POST.get('deleteTarget')
        fromAlbum = self.request.POST.get('fromAlbum')
        fromAlbum = int(fromAlbum)
        if fromAlbum < 0:
            cursor.execute(sql_commands.delete_album, (target, ))
        else:
            cursor.execute(sql_commands.delete_photo, (target, ))
        db.commit()
        self.redirect("/home?redirected=True")


def create_file_path(album_id, photo_id):
    return "/" + BUCKET_NAME + "/" + str(album_id) + "/" + str(photo_id)


def get_user_id_from_cookie(app, cursor):
    user_id = app.request.cookies.get('user_id')
    pw = app.request.cookies.get('identifier')
    if not user_id or not pw:
        return -1
    cursor.execute(
        "SELECT hash_password FROM User WHERE user_id=%s", (user_id, ))
    result = cursor.fetchone()
    if not result:
        return -1
    elif hash_functions.hash_identifier(user_id, result[0]) != pw:
        app.response.delete_cookie("user_id")
        app.response.delete_cookie("identifier")
        return -1
    return int(user_id)


def get_conn_and_cursor():
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute('use main')
    return db, cursor


def close_connection(db, cursor):
    if cursor:
        cursor.close()
    if db:
        db.close()

app = webapp2.WSGIApplication([
    ('/', LoginHandler),
    ('/fakehome', HomeWithMusic),
    ('/home', HomeHandler),
    ('/logout', LogoutHandler),
    ('/register', RegisterHandler),
    ('/setup', MainPage),
    ('/create', AlbumCreateHandler),
    ('/album/.*', AlbumContentHandler),
    ('/upload', UploadHandler),
    ('/delete', DeleteHandler)
], debug=True)
