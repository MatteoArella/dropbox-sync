# dropbox-sync

Systemd compliant service for syncing with dropbox account based on inotify.

The service will watch for any changes made to files in specified directories and will do an automatic backup on dropbox account at shutdown.

## Installation and first usage

1) To allow the `dropbox-sync` service to connect to dropbox account an `access token` must be generated; in order to generate it do the following steps:
   - go to [dropbox for developers](https://www.dropbox.com/developers)
   - sign in to `App console`
   - click on `Create app` and follow guided steps for creating a new app
   - open `Settings` page on the just new app and in the section `Generated access token` click on `Generate`

2. Install the `dropbox-sync` service using
    ```
    ./dropbox-sync install
    ```

3. When asked paste the `access token` generated in the previous steps.

4. Configure service following next section.

5. Start service with
    ```
    ./dropbox-sync start
    ```
    and check its status with
    ```
    ./dropbox-sync status
    ```

## Configuration
Service can be configured modifing a configuration file located in `/etc/dropbox-sync/settings.yml`

```yaml
version: '1.0'
dropbox_sync:
  timestamp_format: '%d-%m-%Y/%H:%M'
  log:
    file_path: '/tmp/logfile'
    log_delete: True
  watcher:
    watchdirs:
      - '/absolute/path/to/directory/to/watch1'
      - '/absolute/path/to/directory/to/watch2'
      - '/absolute/path/to/directory/to/watch3'
    exclude:
      dirs:
        - '/absolute/path/to/directory/to/exclude/from/watch'
      extensions:
        - '.avi'
        - '.mp4'
        - '.mp3'
  sender:
    access_token: <access_token>
    timeout: 900
    exclude:
      max_file_size_limit: '500M'
```

Configuration file must be valid against the following schema:

```yaml
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
```

**It's importand to ALWAYS RESTART service after changes have been made to configuration file**, running the following command:
```
./docker-sync restart
```

## Uninstall
To uninstall `dropbox-sync` service just run
```
./dropbox-sync uninstall
```