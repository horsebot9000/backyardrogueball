# Local server for Backyard Rogueball: same as python -m http.server, but tells the browser not to cache,
# so a new index.html is picked up on the next load.
import http.server, socketserver, sys
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(('127.0.0.1', PORT), H) as httpd:
    print(f'Backyard Rogueball at http://localhost:{PORT}  (close this window to stop)')
    httpd.serve_forever()
