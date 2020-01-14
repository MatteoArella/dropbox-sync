if __name__ == '__main__':
    import pandas as pd
    import os
    from datetime import datetime

    from settings import Settings
    from dropbox_sync_uploader import Uploader

    settings = Settings(settings_file=os.path.join(os.path.dirname(__file__), 'settings.yml'))
    timestamp = datetime.now().strftime(settings.dropbox_sync.timestamp_format)
    logfile = settings.dropbox_sync.log.file_path
    
    uploader = Uploader(settings)

    try:
        df = pd.read_csv(logfile)
        for _, row in df.iterrows():
            remote_file_path = '/backups/{}{}'.format(timestamp, row['filepath'])
            if row['event'] != 'DELETED':
                uploader.upload(row['filepath'], remote_file_path)
            else:
                uploader.delete(remote_file_path)
    except Exception:
        pass
