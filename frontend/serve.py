#!/usr/bin/env python3
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.path = '/index_simple.html'
        return super().do_GET()

os.chdir(r'c:\Users\ACER\Desktop\UsMiniProject\frontend')
server = HTTPServer(('127.0.0.1', 3000), Handler)
print('Resume Verification System is running on http://127.0.0.1:3000/')
print('Backend API: http://127.0.0.1:8000/')
server.serve_forever()
