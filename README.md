# Google Drive File Downloader

Accesses the Google Drive API and lets you single step through each file, giving you the option to download or skip. Non-media files are downloaded as pdf's. Only supports files that can be downloaded as pdf's or audio/video files.

To run:
`python __init__.py [-f fileCount] [-d DOWNLOAD_DIR]`
- `-f`: number of files to fetch from Google Drive API and look at. Default is 10
- `-d`: directory to download files to. Default is current directory

Follow [this tutorial from Google](https://developers.google.com/drive/api/v3/quickstart/python) to make sure you have Google Drive API set up before running.
