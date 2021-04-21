# HomeKit-MiAcPartnerMcn02

专用于丐版粗粮空调伴侣2（lumi.acpartner.mcn02） 接入HomeKit

## Require
  * HAP-python[QRCode]
  * python-miio

## Usage

```bash
    export MCN02_IP= 空调伴侣IP
    export MCN02_TOKEN= 空调伴侣Token
    python3 main.py
```

## Deploy

**Docker部署目前仅适配ARM32v7架构**

```bash
    docker build -t hap_mcn02 .
    docker run -d --network host --name myhap_mcn02 -e MCN02_IP= 空调伴侣IP -e MCN02_TOKEN= 空调伴侣Token hap_mcn02
```

### macvlan network 部署
```bash
    docker network create -d macvlan   --subnet=10.10.10.0/24   --gateway=10.10.10.1  --ip-range=10.10.10.200/29  -o parent=eth0 mvc0
    docker run -d --network mvc0 --name myhap_mcn02 -e MCN02_IP= 空调伴侣IP -e MCN02_TOKEN= 空调伴侣Token hap_mcn02
```


## Notice

1. 需自行获取空调伴侣的IP和Token

    * 一种方法是使用毛子修改版米家APP：

        https://www.kapiba.ru/2017/11/mi-home.html

2. 粗粮坑爹 空调伴侣没有温度传感器 而 `HomeKit` 规定 `HeaterCooler Service` 的`CurrentTemperature` 为必选参数 因此这里只能把目标温度作为当前温度传入 实际使用中发现这样做在使用Siri时可能有Bug 以后会考虑提供接口从外部的温度传感器引入环境温度

3. 还是粗粮坑爹 尽管 `miio` 协议为内网通讯 但实测发现 若给空调伴侣切断外网 则发送指令正常返回但不动作 目前抓包并没有发现空调伴侣对内网扫描的情况发生 至于用不用各位自己掂量吧

4. 还还还是粗粮坑爹 在对米家APP与空调伴侣通讯的 `miio` 协议抓包解析过程中 并没有发现用电量统计的数据字段 推测应该是空调伴侣上报用电量到粗粮服务器上 APP从服务器获取用电量数据 空调伴侣本身不对用电量进行存储 ~~这样的话就没办法用 `miio` 协议去获取用电量数据来展示了~~ **加入电量统计功能 每分钟读取一次负载功率 计算后累加** **5000端口开启web展示**