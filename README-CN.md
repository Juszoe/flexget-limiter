# flexget-limiter
Flexget插件，当系统磁盘或网络速率过高时停止任务

[English](https://github.com/Juszoe/flexget-limiter) | 中文

## 运行环境
- [Flexget](https://flexget.com/)
- Python 3.X 或 Python 2.7 [其他版本解决方案](#version)
- psutil 使用 `pip install psutil` 安装

## 安装插件
1. 安装 psutil
```bash
pip install psutil
```
2. 下载插件 [limiter.py](https://github.com/Juszoe/flexget-limiter/releases)
3. 在 Flexget 配置文件夹下新建 plugins 文件夹，例如：
```
~/.flexget/plugins/                   # Linux
C:\Users\<YOURUSER>\flexget\plugins\  # Windows
```
4. 将插件拷贝至 plugins
5. 若启用了 Web-UI 或守护进程，则重启 Flexget 重新加载配置

## 使用
1. 编辑 Flexget 配置文件，添加`limiter`选项，按照需要进行配置
```yaml
limiter:
  down: 1000       # 下载速度 KB/s
  up: 100          # 上传速度 KB/s
  disk:
    read: 10000    # 磁盘读取速度 KB/s
    write: 10000   # 磁盘写入速度 KB/s
```
当系统参数超过配置值时，当前 Flexget 任务将会停止<br>
`注意：配置可以不完整，只设置你想限制的参数即可`
2. 启动 Flexget
``` bash
flexget execute
```

## 完整配置示例
上传速度超过 10MB/s 时停止任务
```yaml
tasks:
  my-limit-upload-task:
    rss: https://www.example.com/rss
    limiter:
      down: 10240  # 10 x 1024 = 10240
    download: ~/flexget/torrents/
```
磁盘写入速度超过 80MB/s 时停止任务
```yaml
tasks:
  my-limit-write-task:
    rss: https://www.example.com/rss
    limiter:
      disk:
        write: 81920  # 80 x 1024 = 81920
    download: ~/flexget/torrents/
```

## 常见问题
#### 我的 Python 版本是2.X如何使用？
<span id="version"></span>
本插件只支持 Python 3.X 或 Python 2.7 版本，其他版本不可用，请卸载 Flexget 后使用 Python3 重装
```bash
pip uninstall flexget  # 卸载
pip3 install flexget   # 使用pip3安装
```