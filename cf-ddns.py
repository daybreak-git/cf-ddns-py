#!/usr/bin/python
import CloudFlare
import requests
# ==========================================================#
#   Description: 自建Python版基于cloudflareAPI的DDNS      
#   Version: 3.2                                    
#   Author: 蜘蛛子                                 
#   Blog：https://www.zhizhuzi.org                      
#   Telegram: https://t.me/Zhizhuzi                     
#   Github: https://github.com/ZhizhuziQAQ/instance      
#   Latest Update: Fri 30 Jul 2021 09:20:55 AM CST         
# ==========================================================#

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/92.0.4515.131 Safari/537.36 "
}

def clear():
    os.system('clear')


def get_current_ip():
    try:
        r = requests.get("https://api.my-ip.io/ip.json", headers=headers)
        tmp_json = r.json()
        if tmp_json['success'] is True:
            return tmp_json['ip']
    except Exception:
        r_again = requests.get("https://api.ipify.org", headers=headers)
        return r_again.text


def main():
    if CF_Key == "":
        exit("CF_Key 参数为空")
    if CF_Email == "":
        exit("CF_Email 参数为空")
    if CF_Domain == "":
        exit("CF_Domain 参数为空")
    if CF_Domain_Second == "":
        exit("CF_Domain_Second 参数为空")
    if CF_Type == "":
        exit("CF_Type 参数为空")
    if CF_TTL == "":
        exit("CF_TTL 参数为空")
    try:
        cf = CloudFlare.CloudFlare(email=CF_Email, token=CF_Key, raw=True)
    except Exception:
        exit("CF_Key or CF_Email 信息错误")

    try:
        # 返回一个区域列表
        zone = cf.zones.get(params={'name': CF_Domain})
    except Exception:
        exit("CF_Domain 区域信息获取失败")
    zone_id = zone['result'][0]['id']
    params = {'name': CF_Domain_Second}

    try:
        # 获取区域的目标DNS记录
        dns_records = cf.zones.dns_records.get(zone_id, params=params)
    except Exception:
        exit("dns_records 记录获取失败")

    Old_IP = dns_records['result'][0]['content']
    if Old_IP == Current_IP:
        print("DDNS has no change.")
    else:
        dns_record_id = dns_records['result'][0]['id']
        # DNS解析的IP和当前主机IP不一致时，更新记录
        new_dns_record = {
            'zone_id': zone_id,
            'id': dns_record_id,
            'type': CF_Type,
            'name': CF_Domain_Second,
            'content': Current_IP,
            'ttl': CF_TTL,
            'proxied': CF_Force  # 是否强制更新DNS
        }
        try:
            update_dns = cf.zones.dns_records.put(zone_id, dns_record_id, data=new_dns_record)
            print("DDNS更新成功。原IP为：" + Old_IP + "，当前IP为：" + Current_IP)
        except Exception:
            url = "https://api.telegram.org/bot" + TG_BOT_TOKEN + "/sendMessage"
            data = {"chat_id": TG_CHAT_ID, "text": "DDNS更新失败"}
            temp = requests.get(url, headers=headers, json=data)
            exit("DDNS更新失败")
        # 仅Telegram通知
        try:
            if TG_BOT_TOKEN == "" or TG_CHAT_ID == "":
                exit(0)
            # Telegram 通知
            else:
                try:
                    url = "https://api.telegram.org/bot" + TG_BOT_TOKEN + "/sendMessage"
                    data = {"chat_id": TG_CHAT_ID, "text": "DDNS更新成功。原IP为：" + Old_IP + ",当前IP为：" + Current_IP}
                    temp = requests.get(url, headers=headers, json=data)
                except Exception:
                    exit("Telegram 通知失败咯")
        except Exception:
            exit("Telegram 通知失败咯")


if __name__ == '__main__':
    # (必填)CloudFlare 全局密钥
    CF_Key = ""
    # (必填)CloudFlare 邮箱
    CF_Email = ""
    # (必填)所建DDNS的主域名，用于获取区域ID。例如：example.com
    CF_Domain = ""
    # (必填)当服务器IP发送更改时，需要自动更改解析的次一级域名。例如：eg.example.com
    CF_Domain_Second = ""
    # 默认A记录，即ipv4。 因本人无ipv6小鸡，有需求的可以自己改下代码
    CF_Type = "A"
    # (可选)默认设置为1，即ttl为自动，可自行根据需要更改ttl时间，最小值为120s，设置时填写 CF_TTL= "120"
    CF_TTL = "1"
    # 默认False
    CF_Force = False
    # (可选)DDNS更改解析成功时通过TelegramBot通知,为空时即不通知
    TG_CHAT_ID = ""
    # (可选)DDNS更改解析成功时通过TelegramBot通知,为空时即不通知
    TG_BOT_TOKEN = ""
    Current_IP = get_current_ip()
    main()
