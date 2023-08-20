from pydrive.auth import GoogleAuth

gauth = GoogleAuth()
gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.

from pydrive.drive import GoogleDrive

# Create GoogleDrive instance with authenticated GoogleAuth instance.
drive = GoogleDrive(gauth)

# Create GoogleDriveFile instance with title 'Hello.txt'.
file1 = drive.CreateFile({'title': 'Hello.txt'})
file1.Upload() # Upload the file.
print('title: %s, id: %s' % (file1['title'], file1['id']))
# title: Hello.txt, id: {{FILE_ID}}
