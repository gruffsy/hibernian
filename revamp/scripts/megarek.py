import pysftp

sftp_host = "mfservicesstorage.blob.core.windows.net"
sftp_user = "mfservicesstorage.brberg"
sftp_password = "wL5UCJ1vr7UQo3eJjtgvInuRo8+kawvJ"
private_key_path = "brberg"

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

# Opprett en forbindelse
with pysftp.Connection(host=sftp_host, username=sftp_user, private_key=private_key_path, private_key_pass=sftp_password, cnopts=cnopts) as sftp:
    # Liste filer i rotdirectory
    print(sftp.listdir())