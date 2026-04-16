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
KIM_API_BASE = "https://openapi.corp.kuaishou.com"
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
    to_user: str,
    content: str,
    msg_type: str = "text"
) -> bool:
    """
    通过 openapi 平台代理发送消息给指定用户
    需要设置环境变量 KIM_SESSION_COOKIE（从浏览器复制 accessproxy_session）
    """
    session_cookie = os.environ.get("KIM_SESSION_COOKIE", "")
    if not session_cookie:
        print("错误：请设置环境变量 KIM_SESSION_COOKIE")
        print("获取方式：")
        print("  1. 浏览器打开 https://openapi.corp.kuaishou.com")
        print("  2. 开发者工具 → Application → Cookies → 找到 accessproxy_session")
        print("  3. export KIM_SESSION_COOKIE=\"<复制的值>\"")
        return False
    
    # 构建接收者参数
    body_params = {"msgType": msg_type, "content": content}
    if to_user.startswith("kim_"):
        body_params["userId"] = to_user
    elif to_user.startswith("session_"):
        body_params["sessionId"] = to_user
    else:
        body_params["username"] = to_user
    
    # 通过 openapi 平台代理调用
    payload = {
        "appKey": app_key,
        "bodyParams": body_params,
        "headerParams": {},
        "queryParams": {},
        "method": "POST",
        "path": "/openapi/v2/message/send",
        "serverApiCode": "d50455a6-ce0c-4a8b-bd1e-9ae9c18d39e2",
        "serverCode": "dc447d04-09c3-49eb-82b9-da71befb73d9",
        "env": "production",
        "appCode": app_key
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://openapi.corp.kuaishou.com",
        "Referer": "https://openapi.corp.kuaishou.com/",
        "Cookie": f"accessproxy_session={session_cookie}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    }
    
    url = "https://openapi.corp.kuaishou.com/openapi/tools/debugApi"
    print(f"[DEBUG] 请求 URL: {url}")
    print(f"[DEBUG] 目标用户: {to_user}")
    
    import ssl
    ssl_context = ssl.create_default_context()
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT, context=ssl_context) as response:
            result = json.loads(response.read().decode("utf-8"))
            print(f"[DEBUG] 响应: {json.dumps(result, ensure_ascii=False)}")
            # 外层 code=0 表示代理调用成功，再看内层 result
            if result.get("code") == 0:
                inner = result.get("result", {}).get("result", {})
                inner_code = inner.get("code", inner.get("status", -1))
                if inner_code == 0 or str(inner_code).startswith("2"):
                    return True
                else:
                    print(f"API 错误: {inner.get('message', inner)}")
                    return False
            else:
                print(f"代理错误: {result}")
                return False
    
    except urllib.error.HTTPError as e:
        print(f"HTTP 错误: {e.code} - {e.reason}")
        try:
            error_body = e.read().decode("utf-8")
            print(f"响应内容: {error_body}")
        except:
            pass
        return False
    except Exception as e:
        print(f"发送失败: {e}")
        import traceback
        traceback.print_exc()
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
        print("  python kim_notify.py --api --to <用户> --content <消息内容>")
        print("")
        print("参数说明：")
        print("  --to 可以是消息号（kim_xxx）或机器人名称（如「埃姆」）")
        print("")
        print("示例：")
        print('  # 发给机器人「埃姆」')
        print('  python kim_notify.py --api --to "埃姆" --content "日报已更新"')
        print("")
        print('  # 发给消息号')
        print('  python kim_notify.py --api --to "kim_123456" --content "日报已更新"')
        sys.exit(1)
    
    # 解析参数
    args = sys.argv[1:]
    mode = "webhook"
    webhook_url = ""
    to_user = ""
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
        elif arg in ("--to", "--user", "--message-id"):
            to_user = args[i + 1] if i + 1 < len(args) else ""
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
        if not to_user:
            to_user = os.environ.get("KIM_TO_USER", "")
        if not to_user:
            print("错误：请提供目标用户 (--to 或设置 KIM_TO_USER)")
            print("提示：可以是消息号（kim_xxx）或机器人名称")
            sys.exit(1)
        
        app_key, secret_key = get_credentials()
        success = send_api_message(app_key, secret_key, to_user, content)
    
    if success:
        print("✓ 消息发送成功")
    else:
        print("✗ 消息发送失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
