import inotify.adapters as adapters
import inotify.constants as constants
import os
import pandas as pd
from yaml import load
import json

from settings import Settings

def is_whitelisted(settings, file_path):
    if settings.dropbox_sync.watcher.exclude is not None:
        if settings.dropbox_sync.watcher.exclude.extensions is not None:
            if os.path.splitext(file_path)[1] in settings.dropbox_sync.watcher.exclude.extensions:
                return False
        if settings.dropbox_sync.watcher.exclude.dirs is not None:
            for parent_path in settings.dropbox_sync.watcher.exclude.dirs:
                parent_path = os.path.abspath(parent_path)
                child_path = os.path.abspath(file_path)
                if os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path]):
                    return False
    return True

def main(watchdirs, logfile, log_delete=False):
    if os.path.exists(logfile):
        os.remove(logfile)

    mask = (constants.IN_CREATE | constants.IN_CLOSE_WRITE | constants.IN_MODIFY | constants.IN_DELETE | constants.IN_MOVE)
    i = adapters.InotifyTrees(watchdirs, mask=mask)
    event_label = { 'IN_CREATE': 'CREATED', 'IN_MODIFY': 'MODIFIED', 'IN_CLOSE_WRITE': 'MODIFIED', 'IN_DELETE': 'DELETED', 'IN_MOVED_FROM': 'DELETED', 'IN_MOVED_TO': 'RENAMED' }
    tree = {}
    tmp = None
    for (_, type_names, path, filename) in i.event_gen(yield_nones=False):
        filepath = os.path.join(path, filename)
        if filepath == logfile:
            continue
        if not is_whitelisted(settings, filepath):
            continue
        if type_names[0] in event_label:
            tree[filepath] = event_label[type_names[0]]
        if type_names[0] == 'IN_MOVED_FROM':
            tmp = filepath
        else:
            if tmp in tree:
                del tree[tmp]
        df = pd.DataFrame(list(tree.items()), columns=['filepath', 'event'])
        if not log_delete:
            df = df[df.event != 'DELETED']
        df.to_csv(logfile, index=False)

if __name__ == '__main__':
    settings = Settings(settings_file=os.path.join(os.path.dirname(__file__), 'settings.yml'))
    main(watchdirs=settings.dropbox_sync.watcher.watchdirs, logfile=settings.dropbox_sync.log.file_path, log_delete=settings.dropbox_sync.log.log_delete)
