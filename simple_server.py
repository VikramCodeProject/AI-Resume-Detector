#!/usr/bin/env python3
"""
Simple HTTP server for testing - serves frontend with proxy to backend
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import urllib.parse
import urllib.request

class ProxyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/'):
            # Proxy to backend
            backend_path = self.path[4:]  # Remove '/api' prefix
            backend_url = f'http://127.0.0.1:8000{backend_path}'
            try:
                response = urllib.request.urlopen(backend_url)
                self.send_response(response.status)
                for header, value in response.headers.items():
                    self.send_header(header, value)
                self.end_headers()
                self.wfile.write(response.read())
            except Exception as e:
                self.send_error(500, str(e))
        else:
            # Serve static files
            if self.path == '/':
                self.path = '/index.html'
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            # Proxy POST to backend
            backend_path = self.path[4:]
            backend_url = f'http://127.0.0.1:8000{backend_path}'
            
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                req = urllib.request.Request(
                    backend_url,
                    data=body,
                    headers={k: v for k, v in self.headers.items() if k.lower() not in ['host', 'content-length']}
                )
                response = urllib.request.urlopen(req)
                self.send_response(response.status)
                for header, value in response.headers.items():
                    self.send_header(header, value)
                self.end_headers()
                self.wfile.write(response.read())
            except urllib.error.HTTPError as e:
                self.send_error(e.code, e.reason)
            except Exception as e:
                self.send_error(500, str(e))

if __name__ == '__main__':
    os.chdir('/c/Users/ACER/Desktop/UsMiniProject/frontend')
    server = HTTPServer(('127.0.0.1', 3000), ProxyHandler)
    print('Server running on http://127.0.0.1:3000/')
    server.serve_forever()
