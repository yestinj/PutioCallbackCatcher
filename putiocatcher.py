import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as parse
import configparser
import os
import putiopy
import shutil

config_map = dict()


class CallbackCatcher(BaseHTTPRequestHandler):
    # We're only concerned about catching POSTs from put.io.
    def do_POST(self):
        request_path = self.path
        print("\n----- Request Start ----->\n")
        # print(request_path)
        request_headers = self.headers
        content_length = request_headers.getheaders('content-length')
        length = int(content_length[0]) if content_length else 0
        field_data = self.rfile.read(length)
        fields = parse(field_data)
        # print(request_headers)
        # print(field_data)
        print(repr(fields))
        print("<----- Request End -----\n")
        self.send_response(200)

        download_name = fields.get('name')[0]

        # send_push_notification('Put.io notification', 'Download complete callback received for {}'.format(download_name))

        if config_map.get('download_dir'):
            download_dir = config_map['download_dir']

        file_id = fields.get('file_id')
        file_name = download_file(file_id[0], download_dir=download_dir)

        # send_push_notification('Download complete', 'Successfully downloaded {} to server'.format(file_name))

        if config_map.get('archive_dir'):
            archive_dir = config_map.get('archive_dir')
            if not os.path.exists(archive_dir):
                print('Creating directory for achives - {}'.format(archive_dir))
                os.makedirs(archive_dir)

        # If it's a file it's likely compressed, no point redoing it, just move.
        if os.path.isfile(os.path.join(download_dir, file_name)):
            print('File detected, skipping archive, moving to {}'.format(archive_dir))
            if os.path.exists(os.path.join(archive_dir, file_name)):
                print('Error: Existing file in archive directory, aborting and not removing downloaded file!')
                send_push_notification('File exists error',
                                       'Existing file in archive directory, aborting - {}'.format(file_name))
            else:
                shutil.move(os.path.join(download_dir, file_name), os.path.join(archive_dir, file_name))
                print('{} moved to {} successfully!'.format(file_name, archive_dir))
                send_push_notification('Process complete',
                                       'Single file download and archive process complete for {}'.format(file_name))
            return

        # It must be a directory going forward..
        exit = 0
        if config_map.get('archive_command'):
            command = config_map['archive_command']
            command = command.replace('%DOWNLOAD_DIR%', download_dir)
            command = command.replace('%ARCHIVE_DIR%', archive_dir)
            command = command.replace('%NAME%', file_name)
            print('Archiving complete download {}'.format(command))
            exit = os.system(command)
            print('Archiving complete, exit code {}'.format(exit))

            if exit == 0:
                if config_map.get('remove_command'):
                    command = config_map['remove_command']
                    command = command.replace('%DOWNLOAD_DIR%', download_dir)
                    command = command.replace('%NAME%', file_name)
                    print('Removing old files "{}"'.format(command))
                    exit = os.system(command)
                    if exit == 0:
                        print('Removing completed successfully')
                        send_push_notification('Process complete!',
                                               'Archive of {} completed successfully!'.format(file_name))
                    else:
                        print('Error during the removal process!')
                        send_push_notification('Process error!', 'Error while removing: {}'.format(command))
            else:
                print('Error during archive process, aborting')
                send_push_notification('Process error!', 'Error while archving: {}'.format(command))


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
    config = configparser.ConfigParser()
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

        archive_dir = ws_options['archivedir']
        if archive_dir:
            config_map['archive_dir'] = archive_dir
        else:
            config_map['archive_dir'] = './Complete'

        download_dir = ws_options['downloaddir']
        if download_dir:
            config_map['download_dir'] = download_dir
        else:
            config_map['download_dir'] = './Downloads'

    if 'Execute' in config.sections():
        execution = ConfigSectionMap(config, 'Execute')
        config_map['archive_command'] = execution['archivecommand']
        config_map['remove_command'] = execution['removecommand']
        config_map['notify'] = execution['notify']

    if 'PutioCreds' in config.sections():
        putio_creds = ConfigSectionMap(config, 'PutioCreds')
        oauth = putio_creds['oauthtoken']
        config_map['oauth'] = oauth


def send_push_notification(title, message):
    if config_map.get('notify'):
        command = config_map['notify']
        command = command.replace('%TITLE%', title)
        command = command.replace('%MESSAGE%', message)
        print('Sending notification: Title: {}. Message: {}'.format(title, message))
        os.system(command)
    else:
        print('Error: notify command not specified in config file')


def download_file(id, delete_after_download=True, download_dir="./"):
    putio_client = putiopy.Client(config_map['oauth'])
    file = putio_client.File.get(int(id))
    print('Downloading file: {}'.format(str(file)))
    file.download(dest=download_dir, delete_after_download=delete_after_download)
    print('Download complete!')
    return file.name


def write_pid_file():
    pid = str(os.getpid())
    f = open('putiocatcher.pid', 'w')
    f.write(pid)
    f.close()
    return pid


if __name__ == '__main__':

    print('Putio Callback Catcher starting up...')
    pid = write_pid_file()
    print('PID: {}'.format(pid))
    parse_config()

    httpd = HTTPServer((config_map['host'], config_map['port']), CallbackCatcher)
    print("{}: Server Starts - {}:{}".format(time.asctime(), config_map['host'], config_map['port']))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("{}: Server Stops - {}:{}".format(time.asctime(), config_map['host'], config_map['port']))
