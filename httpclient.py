#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, 2021 Hongru Qi  https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        o = urllib.parse.urlparse(url)
        return o
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        splited_data = data.split('\r\n')
        code = splited_data[0].split()[1]
        return int(code)

    def get_headers(self,data):
        splited_data = data.split('\r\n\r\n')
        return splited_data[0]

    def get_body(self, data):
        splited_data = data.split('\r\n\r\n')
        return splited_data[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        url_obj = self.get_host_port(url)
        url_path = url_obj.path
        if not url_path:
            url_path = "/"
        url_port = url_obj.port
        if not url_port:
            url_port = 80

        payload = f'GET {url_path} HTTP/1.1\r\nHost: {url_obj.hostname}\r\n\r\n'

        self.connect(url_obj.hostname, url_port)
        self.sendall(payload)
        full_data = self.recvall(self.socket)
        code = self.get_code(full_data)
        body = self.get_body(full_data)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        url_obj = self.get_host_port(url)
        url_path = url_obj.path
        if not url_path:
            url_path = "/"
        url_port = url_obj.port
        if not url_port:
            url_port = 80

        parse_args = ''
        if (args):
            for arg in args:
                parse_args = parse_args + arg + '=' + args[arg] + '&'
            parse_args = parse_args[:-1]
        args_length = str(len(parse_args))
        
        payload = f'POST {url_path} HTTP/1.1\r\nHost: {url_obj.hostname}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length:{args_length}\r\n\r\n{parse_args}'

        self.connect(url_obj.hostname, url_port)
        self.sendall(payload)
        full_data = self.recvall(self.socket)
        code = self.get_code(full_data)
        body = self.get_body(full_data)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
