#!/usr/bin/env python3
"""
KIM 消息推送脚本
用于 AI 洞察站日报更新后自动推送通知到 KIM 群聊

使用前请设置环境变量：
  export KIM_APP_KEY="your-app-key"
  export KIM_SECRET_KEY="your-secret-key"
  export KIM_WEBHOOK_URL="your-webhook-url"（可选，如果使用 Webhook 模式）
"""

import os
import sys
import json
import time
import hashlib
import hmac
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional

# API 配置
KIM_API_BASE = "https://kim.corp.kuaishou.com"
DEFAULT_TIMEOUT = 10


def get_credentials() -> tuple[str, str]:
    """从环境变量获取凭证"""
    app_key = os.environ.get("KIM_APP_KEY")
    secret_key = os.environ.get("KIM_SECRET_KEY")
    
    if not app_key or not secret_key:
        print("错误：请设置环境变量 KIM_APP_KEY 和 KIM_SECRET_KEY")
        print("\n使用方法：")
        print('  export KIM_APP_KEY="your-app-key"')
        print('  export KIM_SECRET_KEY="your-secret-key"')
        sys.exit(1)
    
    return app_key, secret_key


def generate_signature(app_key: str, secret_key: str, timestamp: str, nonce: str) -> str:
    """
    生成 API 签名
    签名算法：HMAC-SHA256(appKey + timestamp + nonce, secretKey)
    """
    sign_str = f"{app_key}{timestamp}{nonce}"
    signature = hmac.new(
        secret_key.encode("utf-8"),
        sign_str.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return signature


def generate_nonce() -> str:
    """生成随机 nonce（16位）"""
    import random
    import string
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=16))


def send_webhook_message(webhook_url: str, content: str) -> bool:
    """
    通过 Webhook 发送消息（群聊模式）
    这是最简单的发送方式，直接 POST 到 Webhook URL
    """
    payload = {
        "msgType": "text",
        "content": {
            "text": content
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("code") == 0 or result.get("success", False)
    
    except urllib.error.HTTPError as e:
        print(f"HTTP 错误: {e.code} - {e.reason}")
        return False
    except Exception as e:
        print(f"发送失败: {e}")
        return False


def send_api_message(
    app_key: str,
    secret_key: str,
    message_id: str,
    content: str,
    msg_type: str = "text"
) -> bool:
    """
    通过 API 发送消息（指定用户模式）
    使用 /openapi/v2/message/send 接口
    """
    timestamp = str(int(time.time() * 1000))
    nonce = generate_nonce()
    signature = generate_signature(app_key, secret_key, timestamp, nonce)
    
    payload = {
        "appKey": app_key,
        "timestamp": timestamp,
        "nonce": nonce,
        "signature": signature,
        "messageId": message_id,  # 接收者的消息号
        "msgType": msg_type,
        "content": content
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    url = f"{KIM_API_BASE}/openapi/v2/message/send"
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("code") == 0 or result.get("success", False)
    
    except urllib.error.HTTPError as e:
        print(f"HTTP 错误: {e.code} - {e.reason}")
        if e.code == 401:
            print("认证失败，请检查 appKey 和 secretKey 是否正确")
        elif e.code == 403:
            print("权限不足，请确认已申请「发送im消息」接口权限")
        return False
    except Exception as e:
        print(f"发送失败: {e}")
        return False


def format_daily_brief(daily_date: str, summary: str, url: str) -> str:
    """格式化日报简报消息"""
    return f"""📅 AI 洞察日报 · {daily_date}

{summary}

🔗 查看完整内容：{url}

---
埃姆的 AI 洞察 · 深入架构，理解 Agent，追踪应用"""


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法：")
        print("  python kim_notify.py --webhook <webhook-url> --content <消息内容>")
        print("  python kim_notify.py --api --message-id <消息号> --content <消息内容>")
        print("\n示例：")
        print('  python kim_notify.py --webhook "https://kim.corp.kuaishou.com/webhook/xxx" --content "日报已更新"')
        sys.exit(1)
    
    # 解析参数
    args = sys.argv[1:]
    mode = "webhook"
    webhook_url = ""
    message_id = ""
    content = ""
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--webhook":
            mode = "webhook"
            webhook_url = args[i + 1] if i + 1 < len(args) else ""
            i += 2
        elif arg == "--api":
            mode = "api"
            i += 1
        elif arg == "--message-id":
            message_id = args[i + 1] if i + 1 < len(args) else ""
            i += 2
        elif arg == "--content":
            content = args[i + 1] if i + 1 < len(args) else ""
            i += 2
        else:
            i += 1
    
    if not content:
        print("错误：请提供消息内容 (--content)")
        sys.exit(1)
    
    # 发送消息
    if mode == "webhook":
        if not webhook_url:
            webhook_url = os.environ.get("KIM_WEBHOOK_URL", "")
        if not webhook_url:
            print("错误：请提供 Webhook URL (--webhook 或设置 KIM_WEBHOOK_URL)")
            sys.exit(1)
        
        success = send_webhook_message(webhook_url, content)
    
    else:  # api mode
        if not message_id:
            print("错误：请提供消息号 (--message-id)")
            sys.exit(1)
        
        app_key, secret_key = get_credentials()
        success = send_api_message(app_key, secret_key, message_id, content)
    
    if success:
        print("✓ 消息发送成功")
    else:
        print("✗ 消息发送失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
