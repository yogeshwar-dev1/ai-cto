from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'''
        <html>
        <head><title>AI CTO</title></head>
        <body>
            <h1>AI CTO is Running! 🤖</h1>
            <p>Your AI is watching and managing your website automatically.</p>
        </body>
        </html>
        ''')