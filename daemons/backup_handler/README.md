# Several useful bash commands that make it easy and safe to maintain backups that are too old.
* __find backup_dir -type f -name '*YYYY-mm-dd*' | xargs -t -L1 rm__
* __rm -i path/to/dir/with/files/*ddThh:MM*__  - the last confirmation will be requested for each deleted file.
