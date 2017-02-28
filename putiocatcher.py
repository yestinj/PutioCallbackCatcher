import time
import BaseHTTPServer
from urlparse import urlparse, parse_qs

# TODO: Move to config file, or accept as arguments
HOST_NAME = '0.0.0.0' 
PORT_NUMBER = 9001


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # We're only concerned about catching POSTs from put.io.
    def do_POST(self):
	request_path = self.path
        print("\n----- Request Start ----->\n")
        print(request_path)
        request_headers = self.headers
        content_length = request_headers.getheaders('content-length')
        length = int(content_length[0]) if content_length else 0
        field_data = self.rfile.read(length)
	fields = parse_qs(field_data)

        #print(request_headers)
        #print(field_data)
        print(repr(fields))
        print("<----- Request End -----\n")
        
        self.send_response(200)


if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
