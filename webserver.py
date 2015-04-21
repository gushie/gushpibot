import threading
import urlparse
import BaseHTTPServer
import SimpleHTTPServer
from component import Component

WEBSERVER_PORT = 80

class Webserver(Component):
    class WebHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            if self.path == "/":
                self.path = "/index.html"
            return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

        def do_POST(self):
            self.wfile.write(self.server.post_handlers[self.path[1:]]())

    def __init__(self):
        self.post_handlers = {}
        self.httpd = None

    def serve(self):
        self.httpd = BaseHTTPServer.HTTPServer(('0.0.0.0', WEBSERVER_PORT), Webserver.WebHandler)
        self.httpd.post_handlers = self.post_handlers
        self.t = threading.Thread(target=self.httpd.serve_forever)
        self.t.daemon = False
        self.t.start()

    def cleanup(self):
        if self.httpd:
            self.httpd.shutdown()
