import socketserver

import environs
from environs import Env

from HttpHandler import MyHandler

if __name__ == "__main__":
    env = Env()
    env.read_env()
    try:
        PORT = int(env("PORT"))
    except environs.EnvError:
        PORT = 8000

    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print("serving at port", PORT)
        try:
            httpd.serve_forever()
        finally:
            httpd.server_close()