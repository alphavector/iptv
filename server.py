from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler


class MyServer(SimpleHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        # self.send_header('Content-Disposition', 'attachment; filename="file.pdf"')
        self.end_headers()

        # not sure about this part below

        with open('playlist.sorted.head.m3u', 'rb') as fd:
            self.wfile.write(fd.read())


myServer = HTTPServer(('localhost', 8080), MyServer)
myServer.serve_forever()
myServer.server_close()
