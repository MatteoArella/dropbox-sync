import dropbox
import os
import re

class Uploader:
    def __init__(self, settings):
        self.client = dropbox.Dropbox(settings.dropbox_sync.sender.access_token, settings.dropbox_sync.sender.timeout)
        self.client.users_get_current_account()
        self.settings = settings

    def _is_whitelisted(self, file_path):
        weights = {'B': 1, 'K': 1000, 'KB': 1000, 'KiB': 1024, 'M': 1000000, 'MB': 1000000, 'MiB': 1024*1024, 'G': 1000000000, 'GB': 1000000000, 'GiB': 1024*1024*1024}
        if self.settings.dropbox_sync.sender.exclude is not None and self.settings.dropbox_sync.sender.exclude.max_file_size_limit is not None:
            match = re.search(r'([0-9]*)([a-zA-Z]*)', self.settings.dropbox_sync.sender.exclude.max_file_size_limit)
            if match:
                max_size = int(match.group(1))
                suffix = match.group(2).upper()
                file_size = os.path.getsize(file_path)
                if file_size >= max_size * weights.get(suffix, 1):
                    return False
        return True

    def upload(self, file_path, target_path, chunk_size=4*1024*1024):
        try:
            if not self._is_whitelisted(file_path):
                return
            with open(file_path, 'rb') as f:
                file_size = os.path.getsize(file_path)
                if file_size <= chunk_size:
                    self.client.files_upload(f.read(), target_path, mode=dropbox.files.WriteMode.overwrite)
                else:
                    upload_session_start_result = self.client.files_upload_session_start(f.read(chunk_size))
                    cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id, offset=f.tell())
                    commit = dropbox.files.CommitInfo(path=target_path, mode=dropbox.files.WriteMode.overwrite)
                    while f.tell() < file_size:
                        if (file_size - f.tell()) <= chunk_size:
                            self.client.files_upload_session_finish(f.read(chunk_size), cursor, commit)
                        else:
                            self.client.files_upload_session_append_v2(f.read(chunk_size), cursor)
                            cursor.offset = f.tell()
        except Exception:
            pass
    
    def delete(self, file_path):
        try:
            self.client.files_delete(file_path)
        except Exception:
            pass
