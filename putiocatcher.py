import time
import BaseHTTPServer
from urlparse import urlparse, parse_qs
import ConfigParser
import os
import putiopy

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

        download_name = fields.get('name')

        if config_map.get('execute_command'):
            command = config_map['execute_command']
            command = str(command).replace('%NAME%', download_name[0])
            print('Executing {}'.format(command))
            os.system(command)

        file_id = fields.get('id)')
        download_file(file_id)


def ConfigSectionMap(config, section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
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

    if 'Execute' in config.sections():
        execution = ConfigSectionMap(config, 'Execute')
        command = execution['command']
        config_map['execute_command'] = command
        # print('cfg: Got command to execute: {}'.format(command))

    if 'PutioCreds' in config.sections():
        putio_creds = ConfigSectionMap(config, 'PutioCreds')
        oauth = putio_creds['oauthtoken']
        config_map['oauth'] = oauth


def download_file(id, delete_after_download=True):
    putio_client = putiopy.Client(config_map['oauth'])
    file = putio_client.File.get(int(id))
    print('Downloading file: {}'.format(str(file)))
    file.download(dest="./Downloads/", delete_after_download=delete_after_download)
    print('Download complete!')


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
