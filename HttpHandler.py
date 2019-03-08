import http.server
import urllib
import urllib.request

import hashlib
import uuid

import sqlite3

from threading import Thread

import smtplib
from environs import Env
from email.mime.text import MIMEText
import email.utils


class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        if "/check?" in self.path:
            answer = {
                "status": "not found"
            }

            if "?" in self.path:
                find_key_id = False
                for key, id in dict(urllib.parse.parse_qsl(self.path.split("?")[1], True)).items():
                    if key == "id":
                        find_key_id = True
                        conn = sqlite3.connect("result.db")
                        cursor = conn.cursor()
                        try:
                            cursor.execute('SELECT status, email, md5, url FROM results WHERE id=?', (id,))
                            result_execute = cursor.fetchone()
                            if result_execute is not None:

                                result_execute = list(result_execute)
                                answer["status"] = result_execute[0]
                                if answer["status"] == "done":
                                    answer["md5"] = result_execute[2]
                                    answer["url"] = result_execute[3]
                                    self.send_response(200)
                            else:
                                self.send_response(404)
                        except sqlite3.IntegrityError as e:
                            print('sqlite error: ', e)
                        conn.commit()
                        conn.close()
                if not find_key_id:
                    self.send_response(400)
            else:
                self.send_response(400)
            self.wfile.write(str(answer).encode('utf-8'))

        else:
            self.send_response(400)

    def send_email(self, url, md5, post_email):
        try:
            env = Env()
            env.read_env()
            from_email = env("EMAIL")
            password_from_email = env("PASSWORD")
            smtp = env("SMTP")
        except Exception as e:
            print("error .env: ", e)
            return

        msg = MIMEText(str("url: " + url + "\nmd5: " + md5))
        msg['To'] = email.utils.formataddr(('Recipient Name', post_email))
        msg['From'] = email.utils.formataddr(('Md5 light', from_email))
        msg['Subject'] = 'Md5'
        server = smtplib.SMTP_SSL(smtp)
        server.login(from_email, password_from_email)

        try:
            server.sendmail(from_email, [post_email], msg.as_string())
        except Exception as e:
            print("error email or password in .env or POST email: ", e)
        finally:
            server.quit()

    def md5_sum(self, id, url, post_email):
        md5 = None
        try:
            content = urllib.request.urlopen(url)
            d = hashlib.md5()
            for line in content:
                d.update(line)
            md5 = str(d.hexdigest())
        except Exception as e:
            print(e)

        conn = sqlite3.connect("result.db")
        cursor = conn.cursor()
        if md5 is not None:
            try:
                cursor.execute('UPDATE results SET status=?, md5=? WHERE id=?', ('done', md5, id))
                self.send_email(url, md5, post_email)
            except sqlite3.IntegrityError as e:
                print('sqlite error: ', e)
        else:
            try:
                cursor.execute('UPDATE results SET status=? WHERE id=?', ('fail', id))
            except sqlite3.IntegrityError as e:
                print('sqlite error: ', e)
        conn.commit()
        conn.close()

    def do_POST(self):
        if self.path == "/submit":
            data_elem = {
                "id": str(uuid.uuid4()),
            }

            post_url = ""
            post_email = ""
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            post_body = post_body.decode("utf-8")
            post_body = post_body.split("&")
            for post_variable in post_body:
                post_variable = post_variable.split("=")
                if len(post_variable) > 1 and post_variable[0] == "url":
                    post_url = post_variable[1]
                if len(post_variable) > 1 and post_variable[0] == "email":
                    post_email = post_variable[1]


            conn = sqlite3.connect("result.db")
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO results (id, email, status, md5, url) VALUES (?,?,?,?,?)',
                          (data_elem['id'], post_email, 'running', "", post_url))
            except sqlite3.IntegrityError as e:
                print('sqlite error: ', e)
            conn.commit()
            conn.close()

            t1 = Thread(target=self.md5_sum, args=(data_elem['id'], post_url, post_email), daemon=True)
            t1.start()

            self.wfile.write(str(data_elem).encode("utf-8"))
            self.send_response(200)
        else:
            self.send_response(404)
