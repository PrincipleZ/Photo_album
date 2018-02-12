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

CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')

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

        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            passwd=CLOUDSQL_PASSWORD)

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        db = MySQLdb.connect(
            host='127.0.0.1', user=CLOUDSQL_USER, passwd=CLOUDSQL_PASSWORD)

    return db

db = connect_to_cloudsql()
cursor = db.cursor()
cursor.execute('use main')


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
        cursor.execute('SHOW VARIABLES')

        for r in cursor.fetchall():
            self.response.write('{}\n'.format(r))


class RegisterHandler(webapp2.RequestHandler):

    def get(self):
        self.redirect('/')

    def post(self):
        email = self.request.get('email')
        pw = self.request.get('key')
        username = self.request.get('username')
        cursor.execute("SELECT * FROM User WHERE email='{}'".format(email))
        result = cursor.fetchone()
        if not result:
            cursor.execute(
                "INSERT INTO User (name, email, password) VALUES ('{}', '{}', '{}')".format(
                    username, email, pw))
            cursor.execute(
                "SELECT user_id FROM User WHERE email='{}'".format(email))
            user_id = cursor.fetchone()[0]
            self.response.set_cookie('user_id', str(user_id), max_age=360)
            self.redirect('/home', self.response)
        else:
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

        email = self.request.get('email')
        pw = self.request.get('key')
        cursor.execute(
            "SELECT password, name, user_id FROM User WHERE email='{}'".format(email))
        result = cursor.fetchone()
        if not result or result[0] != pw:
            template = JINJA_ENVIRONMENT.get_template('template/login.html')
            self.response.out.write(template.render(
                {"ERROR": "Invalid email/password combination, please try again."}))
        else:
            self.response.set_cookie('user_id', str(result[2]), max_age=360)
            self.redirect('/home', self.response)


class HomeHandler(webapp2.RequestHandler):

    def get(self):
        user_id = self.request.cookies.get('user_id')
        if not user_id:
            return self.redirect('/')
        user_id = int(user_id)
        cursor.execute(
            "SELECT name FROM User WHERE user_id = {}".format(user_id))
        username = cursor.fetchone()[0]
        cursor.execute(sql_commands.get_albums(user_id))
        results = cursor.fetchall()
        render_var = {"USERNAME": username, "ALBUMS": results}
        template = JINJA_ENVIRONMENT.get_template('template/usermain.html')
        self.response.out.write(template.render(render_var))


class LogoutHandler(webapp2.RequestHandler):

    def get(self):
        self.response.delete_cookie("user_id")
        self.redirect('/', self.response)


class AlbumCreateHandler(webapp2.RequestHandler):

    def get(self):
        self.redirect('/home')

    def post(self):
        name = self.request.get('albumname')
        desc = self.request.get('description')
        user_id = self.request.cookies.get('user_id')
        user_id = int(user_id)
        print "user_ID" + str(user_id)

        cursor.execute(sql_commands.create_album(name, desc, user_id))
        print "here"
        self.redirect('/home')

app = webapp2.WSGIApplication([
    ('/', LoginHandler),
    ('/home', HomeHandler),
    ('/logout', LogoutHandler),
    ('/register', RegisterHandler),
    ('/setup', MainPage),
    ('/create', AlbumCreateHandler)
], debug=True)
