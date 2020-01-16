# flexget-limiter
A flexget plugin for stop task when high I/O or network usage

English | [中文](https://github.com/Juszoe/flexget-limiter/blob/master/README-CN.md)

## Requirement
- [Flexget](https://flexget.com/)
- Python 3.X or Python 2.7 [Other version solution](#version)
- psutil, Please use `pip install psutil` to install

## Install
1. Install psutil
```bash
pip install psutil
```
2. Download plugin [limiter.py](https://github.com/Juszoe/flexget-limiter/releases)
3. Create a new `plugins` folder under the Flexget configuration folder, for example:
```
~/.flexget/plugins/                   # Linux
C:\Users\<YOURUSER>\flexget\plugins\  # Windows
```
4. Copy the limiter.py to the `plugins` folder
5. If Web-UI or daemon is enabled, please restart Flexget to reload the configuration

## Usage
1. Editing the Flexget configuration. Add `limiter` option and configure as needed
```yaml
limiter:
  down: 1000       # download speed KB/s
  up: 100          # upload speed KB/s
  disk:
    read: 10000    # disk read speed KB/s
    write: 10000   # disk write speed KB/s
```
advanced
```yaml
limiter:
  wait: 1          # detection time, second, default: 1s
  reject: no       # reject all items, yes or no, default: no
```
When the system parameter exceeds the configured value, the current Flexget task will stop<br>
`Note: The configuration can be incomplete, just set the parameters you want to limit`

2. Start Flexget
``` bash
flexget execute
```

## Configuration example
Stop task when upload speed exceeds 10MB/s
```yaml
tasks:
  my-limit-upload-task:
    rss: https://www.example.com/rss
    limiter:
      down: 10240  # 10 x 1024 = 10240
    download: ~/flexget/torrents/
```
Stop task when disk write speed exceeds 80MB/s
```yaml
tasks:
  my-limit-write-task:
    rss: https://www.example.com/rss
    limiter:
      disk:
        write: 81920  # 80 x 1024 = 81920
    download: ~/flexget/torrents/
```

## Q&A
#### How can I use because my python version is 2.X ?
<span id="version"></span>
This plugin only supports Python 3.X or Python 2.7. Other versions are not available. Please uninstall Flexget and install with Python3.
```bash
pip uninstall flexget  # uninstall
pip3 install flexget   # install with pip3
```