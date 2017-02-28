import time
import BaseHTTPServer
from urlparse import urlparse, parse_qs
import ConfigParser

config_map = dict()


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

        # print(request_headers)
        # print(field_data)
        print(repr(fields))
        print("<----- Request End -----\n")

        self.send_response(200)


def ConfigSectionMap(config, section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1


def parse_config(cfg_file_path='pcc.config'):
    config = ConfigParser.ConfigParser()
    config.read(cfg_file_path)
    if 'WebServer' in config.sections():
        ws_options = ConfigSectionMap(config, "WebServer")
        host = ws_options['host']
        if host:
            config_map['host'] = host
        else:
            config_map['host'] = "0.0.0.0"
        print('cfg: Set hostname to {}'.format(config_map['host']))

        port = ws_options['port']
        if port:
            config_map['port'] = int(port)
        else:
            config_map['port'] = 9001
        print('cfg: Set port number to {}'.format(config_map['port']))


if __name__ == '__main__':
    parse_config()
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((config_map['host'], config_map['port']), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (config_map['host'], config_map['port'])
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (config_map['host'], config_map['port'])