# KIM 消息推送配置指南

## 一、获取 Webhook URL（群聊模式）

1. 在 KIM 客户端创建或进入目标群聊
2. 点击群设置 → 群机器人 → 添加机器人
3. 选择「自定义机器人」
4. 设置机器人名称（如「AI 洞察站」）
5. 复制生成的 **Webhook URL**

## 二、获取 appKey 和 secretKey（API 模式）

1. 访问快手开放平台（内网）：https://open.corp.kuaishou.com
2. 创建应用，选择「KIM 开放能力」
3. 在应用详情页获取：
   - **appKey**
   - **secretKey**
4. 申请接口权限：
   - 服务名称：KIM 开放能力
   - 接口：`发送im消息` (`/openapi/v2/message/send`)

## 三、配置环境变量

在 `~/.zshrc` 或 `~/.bashrc` 中添加：

```bash
# KIM 推送凭证
export KIM_APP_KEY="你的appKey"
export KIM_SECRET_KEY="你的secretKey"
export KIM_WEBHOOK_URL="你的webhook-url（可选）"
```

然后执行：

```bash
source ~/.zshrc
```

## 四、使用方式

### Webhook 模式（推荐，用于群聊）

```bash
python scripts/kim_notify.py \
  --webhook "https://kim.corp.kuaishou.com/webhook/xxx" \
  --content "日报已更新：https://ammpnk.github.io/ai-insight/"
```

### API 模式（用于指定用户）

```bash
python scripts/kim_notify.py \
  --api \
  --message-id "目标用户的消息号" \
  --content "日报已更新"
```

## 五、集成到更新脚本

在 `update.sh` 中添加：

```bash
# 推送通知
if [ "$PUSH_NOTIFY" = "true" ]; then
  python scripts/kim_notify.py \
    --webhook "$KIM_WEBHOOK_URL" \
    --content "📰 AI 洞察日报已更新\n\n$(date +%Y-%m-%d)\nhttps://ammpnk.github.io/ai-insight/"
fi
```

## 六、安全提醒

⚠️ **不要**将 appKey 和 secretKey 提交到 Git 仓库！

`.gitignore` 中已添加：
```
.env
*_key.txt
secrets.*
```

---

**参考资料**
- Kim Msg Account Skill: https://clawhub.ai/leegodamn/kim-msg-account
- 快手开放平台文档（内网）
