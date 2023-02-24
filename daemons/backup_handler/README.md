# Example of a program run command:
```
python backup_handler --config=./backup_handler/configs/base.json
```


# Several useful bash commands that make it easy and safe to maintain backups that are too old.

* ``` find backup_dir -type f -name '*YYYY-mm-dd*' | xargs -t -L1 rm ```
* ``` rm -i path/to/dir/with/files/*ddThh:MM* ```  - the last confirmation will be requested for each deleted file.
