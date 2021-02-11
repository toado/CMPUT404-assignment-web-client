#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

    def print_response(self, response):
        print("\n" + "="*50  + "\n" + response + "="*50 +"\n")

    # NOTE: (SOURCE & USE CASE)
    # https://docs.python.org/3/library/urllib.parse.html
    # Parsing url for (host, port, path)
    def get_host_port_path(self, url):
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname

        # If port not specified, default to "80"
        if parsed_url.port:
            port = parsed_url.port
        else:
            port = 80

        # If path not specified, default to "/"
        if parsed_url.path:
            path = parsed_url.path
        else:
            path = "/"
            
        return (host, port, path)

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split(" ")[1])

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return(data.split("\r\n\r\n")[1])
    
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
        return buffer.decode()

    def GET(self, url, args=None):
        host, port, path = self.get_host_port_path(url)
        self.connect(host, port)

        request_header = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Connection: close\r\n\r\n"
        )
        self.sendall(request_header)
        response = self.recvall(self.socket)
        self.close()

        self.print_response(response)
        return HTTPResponse(self.get_code(response), self.get_body(response))

    def POST(self, url, args=None):
        host, port, path = self.get_host_port_path(url)
        self.connect(host, port)

        body_parameters = ""
        if args:
            body_parameters = urllib.parse.urlencode(args)

        request_header = (
            f"POST {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Content-Length: {len(body_parameters)}\r\n"
            f"Content-Type: application/x-www-form-urlencoded\r\n"
            f"Connection: close\r\n\r\n"
            f"{body_parameters}"
        )   
        self.sendall(request_header)
        response = self.recvall(self.socket)
        self.close()

        self.print_response(response)
        return HTTPResponse(self.get_code(response), self.get_body(response))

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
