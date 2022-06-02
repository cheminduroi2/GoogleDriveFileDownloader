import argparse
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_cmd_line_args():
    parser = argparse.ArgumentParser(description='Google Drive File Downloader Configuration')
    # number of files to retrieve
    parser.add_argument('-f', dest='file_count', type=int, default=10, help='number of files to retrieve')
    #directory to download files to. default is current directory
    parser.add_argument('-d', dest='dir', default=os.getcwd(), help='directory to download files to')
    return parser.parse_args()

def init_drive_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

#can be extended for beetter support of additional mime types
def get_export_mime_type(mime_type):
    if mime_type == 'application/vnd.google-apps.video':
        return 'video/mp4'
    if mime_type == 'application/vnd.google-apps.audio':
        return 'audio/mp3'
    return 'application/pdf'

def download_file(drive_service, dl_file, dest_path):
    file_mime_type = get_export_mime_type(dl_file['mimeType'])
    request = drive_service.files().export(fileId=dl_file['id'], mimeType=file_mime_type).execute()
    #could break depending on what supported mime types are added to get_export_mime_type()
    file_dest = os.path.join(dest_path, dl_file['name'] + '.' + file_mime_type[-3:])
    #in case user enters a directory that is not yet existent, create it
    os.makedirs(os.path.dirname(file_dest), exist_ok=True)
    with open(file_dest, 'wb') as f:
        f.write(request)
    print('Download finished\n')

def get_files(drive_service, file_count):
    # Call the Drive v3 API
    return drive_service.files().list(
        pageSize=file_count,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute().get('files', [])

def download_files(drive_service, files, download_options):
    #skip these since all non-audio and non-video files will get saved as pdfs
    blacklisted_mime_types = ['application/vnd.google-apps.unknown', 'application/vnd.google-apps.drive-sdk', 'application/vnd.google-apps.map', 'application/vnd.google-apps.folder']
    print("Hello, here are your files. Press 'Q' to quit at any tme:\n")
    for drive_file in files:
        if drive_file['mimeType'] in blacklisted_mime_types: continue
        shouldDownload = input(u"Download the file: {0} ({1})? ('Y/y' or 'N/n')\n".format(drive_file['name'], drive_file['id']))
        while not isinstance(shouldDownload, str) or shouldDownload.lower() not in ['y', 'n', 'q']:
            print("The response must be either 'Y' or 'y' for yes, 'N' or 'n' for no, or 'Q' or 'q' to quit")
            shouldDownload = input(u"Download the file: {0} ({1})? ('Y/y' or 'N/n')\n".format(drive_file['name'], drive_file['id']))
        shouldDownload = shouldDownload.lower()
        if shouldDownload == 'y':
            print('Starting download...')
            download_file(drive_service, drive_file, download_options.dir)
        elif shouldDownload == 'n':
            print('Not Downloading!\n')
        elif shouldDownload == 'q':
            break

def main():
    #gets options for downloading files
    cmd_line_args = get_cmd_line_args()
    service = init_drive_service()
    #get files from google drive
    items = get_files(service, cmd_line_args.file_count)
    if not items:
        print('No files found.')
    else:
       download_files(service, items, cmd_line_args)
    print('Exiting...')

if __name__ == '__main__':
    main()