#!/usr/bin/env bash
access_token=$1
output_file=$2
cat <<EOF > $output_file
version: '1.0'
dropbox_sync:
  timestamp_format: '%d-%m-%Y/%H:%M'
  log:
    file_path: '/tmp/'
    file_name: 'logfile'
    log_delete: True
  watcher:
    watchdirs:
    exclude:
      dirs:
      extensions:
        - '.avi'
        - '.mp3'
        - '.mp4'
  sender:
    access_token: $access_token
    timeout: 900
    exclude:
      max_file_size_limit: '500M'
EOF