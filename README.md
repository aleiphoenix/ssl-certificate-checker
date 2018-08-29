## SSL证书过期检查

### 运行环境

Python3.2+

### 命令行选项

查看

默认15天内报警，每24小时检查一次

```bash
$ python3 checker.py --help
```

### 配置文件

`config.py` 直接提交进git 部署只需要拉取最新代码即可

主机列表两个元组的含义为

```
# hostname 为 SSL 证书里主机明，即Command Name或者SNI
# connect 为实际连接到哪台服务器
(hostname, connect)
```

### 功能

根据配置好的主机列表，检查SSL有效期，低于设置的时间时，通过 voicepipe 接口通知钉钉群报警
