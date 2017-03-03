# PutioCallbackCatcher
A callback catcher for the put.io service

The aim of this project is to provide a simple to use Python server which can be run on a server and is capable of receiving and processing "download complete" notifications from the Put.io service.

This tool specifically has the functionality to download the completed file/folder, and additional custom commands may be defined in the config file to enable archiving, moving, deletion, and notification of completed downloads.

# Usage

The start.sh and stop.sh scripts may be used as a convenience to start and stop the putiocatcher.py application. Starting the server using this method causes is to be backgrounded, and for stdout and stderr to be redirected to appropriately named files.

The application has sensible defaults, as can be seen in the `pcc.config` file, as well as in the source code. However, at a minimum you will need to enter your Put.io OAuth token in the config file in order to enable downloads of completed files.

Example usage:

`./start.sh`
`./stop.sh`

## Put.io OAuth Token 

The easiest way I have found to get a put.io OAuth token to use with this application is to:

1. Visit https://put.io
2. Login to your account if necessary
3. Navigate to Settings along the left hand menu bar.
4. Scroll down, and click on "Manage OAuth Applications"
5. Click the "CREATE A NEW OAUTH APP" button.
6. Enter whatever you like (for the most part) and click Save
7. Click on the Key icon to the right of the Application name you just created.
8. This will open up a new page which will contain a field entitled "OAUTH TOKEN", copy the value of this field, it is the OAuth token that you need to put in the `pcc.config` file.

## Config File

The config file contains mandatory as well as optional sections, the sections currently supported are: WebServer, Execute, and PutioCreds.

For example, the WebServer section allows you to set the hostname/IP on which the server will listen, the port that it will listen on, as well as the download directory (where new files will go), and the archive directory (where completed files will be moved/archived to).

```
[WebServer]
Host: 0.0.0.0
Port: 9001
ArchiveDir: ./Complete/
DownloadDir: ./Downloads/
```

The PutioCreds section is where you need to enter your OAuth token. Fill it in on the right hand side of the OauthToken key:

```
[PutioCreds]
OauthToken: <Your Putio OAuth token>
```

The Execute section allows you to specify what shell commands to run in order to perform certain actions. Sensible defaults have been provided for archiving and removing, however you will need to update the Notify command with your own token and userid, or replace it with another command entirely.

*Note:* While the application should work without any of these config options defined, it has not been thoroughly tested. This is a work in progress.

```
[Execute]
Notify: curl -s -F "token=<Your pushover token>" \
    -F "user=<Your user token>" \
    -F "title=%TITLE%" \
    -F "message=%MESSAGE%" https://api.pushover.net/1/messages.json > /dev/null 2>&1
ArchiveCommand: tar -cf "%ARCHIVE_DIR%%NAME%.tar" "%DOWNLOAD_DIR%%NAME%"
RemoveCommand: rm -rvf "%DOWNLOAD_DIR%%NAME%"
```

The command specified in Notify will be run with an appropriate title and message substituted at certain points in the server processing process. Such as when a new POST request arrives from put.io, when the download of a new request is completed, and when archiving and removal has completed. Some error conditions may also trigger a notification. You are encourage to extend this as you like.

If the archive command is specified, whenever a directory is downloaded it will be archived (using tar with no compression) and then moved to the archive directory. If the completed download is not a directory, and is a single file, it will simply be moved to the archive directory if specified.

The remove command will only be run after a download has been successfully completed, and archived (so only directories), and will remove the directory that was downloaded initially from the download directory. This aims to allow for all complete 'processed' downloads to be moved to their own directory for further processing, and leave the download directory for new incoming downloads.

The %ARCHIVE_DIR%, %DOWNLOAD_DIR%, and %NAME% sequences show in archive command and remove command and replaced in the Python code by the actual values of these. The name represents the actual name of the file downloaded from put.io.

## Configuring Put.io to use your callback server

Once you have your server configured and up and running the last step is to specify the address of your server in the put.io settings.

In order to do this you will either need to run the server on a physcial or virtual server that has a public IP address, and ensure that your firewall is set to allow the incoming connection. Or you if you run this on your home Internet connection where you have a dynamic IP address and are behind a NAT router, you will need to port forward the relevant port in your router, and make use of a dynamic DNS service to ensure that the callback always reaches you.

Information regarding port forwarding, dynamic DNS, NAT, and firewalls can be found online and will not be repeated here.

Perform the following steps to configure your put.io account to notify your server of completed downloads:

1. Visit https://put.io and login if necessary.
2. Click on Settings on the left hand menu bar.
3. Scroll down to the "CALLBACK URL" field.
4. Enter the web address of the server on which you are running PutioCallbackCatcher. You may use either an IP address or a domain name, be sure to include the port, for e.g. http://127.0.0.1:9001/
5. Click Save.

Once you have done this, you should test to ensure it works as expected.

1. Start up your server and tail the stdout log file `./start.sh; tail -f stdout.log`
2. Add a new download to your Put.io account.
3. Watch your server logs and you should see a new POST request come in once the download on put.io is complete.
4. Depending how you've configured your server, the request will trigger download, archive, and push notification actions.

If you are having any trouble be sure to check the `stderr.log` file to troubleshooting.
