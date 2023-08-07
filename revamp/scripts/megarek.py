import pysftp

sftp_host = "mfservicesstorage.blob.core.windows.net"
sftp_user = "mfservicesstorage.brberg"
# sftp_password = "wL5UCJ1vr7UQo3eJjtgvInuRo8+kawvJ"
private_key_path = "filezilla.ppk"

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

# Opprett en forbindelse
with pysftp.Connection(host=sftp_host, username=sftp_user, private_key=private_key_path, cnopts=cnopts) as sftp:
    # Liste filer i rotdirectory
    print(sftp.listdir())