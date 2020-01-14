from yaml import load
import json
from jsonschema import validate
import os

class Settings:
    class NestedWrapper(object):
        def __init__(self, dictionary):
            def _traverse(key, element):
                if isinstance(element, dict):
                    return key, Settings.NestedWrapper(element)
                else:
                    return key, element

            objd = dict(_traverse(k, v) for k, v in dictionary.items())
            self.__dict__.update(objd)

    schema = """
        type: object
        required:
          - "version"
          - "dropbox_sync"
        properties:
          version:
            type: string
            description: "Configuration schema version"
          dropbox_sync:
            type: object
            description: "Base configuration file entrypoint"
            required:
              - "timestamp_format"
              - "log"
              - "watcher"
              - "sender"
            properties:
              timestamp_format:
                type: string
                description: "Timestamp format for backup base folder"
              log:
                type: object
                required:
                  - "file_path"
                  - "log_delete"
                properties:
                  file_path:
                    type: string
                    description: "Location for file storing file system modifies"
                  log_delete:
                    type: boolean
                    description: "Apply file deletions also on dropbox account"
              watcher:
                type: object
                required:
                  - "watchdirs"
                properties:
                  watchdirs:
                    type: array
                    description: "Folders to watch for file changes"
                    items:
                      type: string
                  exclude:
                    type: object
                    properties:
                      dirs:
                        type: array
                        description: "Folders to exclude from watching"
                        items:
                          type: string
                      extensions:
                        type: array
                        description: "File extensions to exclude from sync"
                        items:
                          type: string
              sender:
                type: object
                required:
                  - "access_token"
                properties:
                  access_token:
                    type: string
                    description: "Dropbox account access token"
                  timeout:
                    type: integer
                    description: "Timeout for dropbox connection initialization"
                  exclude:
                    type: object
                    properties:
                      max_file_size_limit:
                        type: string
                        description: "File size limit for dropbox uploading"
    """

    @staticmethod
    def _validate(instance):
        validate(instance, load(Settings.schema))

    def __init__(self, **kwargs):
        default_settings_file = os.path.join(os.path.dirname(__file__), 'settings.yml')
        settings_file = kwargs.get('settings_file', default_settings_file)
        with open(settings_file) as file:
            settings = load(file)
            Settings._validate(settings)
            self.settings = Settings.NestedWrapper(settings)
            
    def __getattr__(self, attr):
        return getattr(self.settings, attr, None)

    def __dict__(self):
        return json.loads(json.dumps(self.settings, default=lambda o: o.__dict__))

    def __str__(self):
        return str(dict(self))

    def __repr__(self):
        return str(self)