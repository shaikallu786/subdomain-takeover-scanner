# Security Alert: Exposed Telegram Bot Token

## ⚠️ CRITICAL: Token was exposed in git history

Your Telegram bot token was accidentally committed to the repository. Follow these steps immediately:

## 🔧 Immediate Actions Required

### 1. Revoke the Exposed Token
- Go to [@BotFather](https://t.me/BotFather) on Telegram
- Send `/revoke` to disable the current token
- Send `/token` to generate a new token
- **DO NOT** use the old token anymore

### 2. Set Up Environment Variables
```bash
# Create .env file (copy from .env.example)
cp .env.example .env

# Edit .env with your new token and chat ID
# TELEGRAM_BOT_TOKEN=your_new_token_here
# TELEGRAM_CHAT_ID=your_chat_id_here
```

### 3. Clean Git History (Optional but Recommended)
```bash
# Remove secrets from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch src/scanner.py get_chat_id.py" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (WARNING: This rewrites history)
git push origin --force --all
git push origin --force --tags
```

## 🛡️ Prevention for Future

- ✅ Environment variables are now used instead of hardcoded secrets
- ✅ `.gitignore` created to prevent future leaks
- ✅ `.env.example` template provided
- ✅ Never commit `.env` files

## 📋 Quick Setup After Token Rotation

1. **Get new token from BotFather**
2. **Message your bot on Telegram**
3. **Run**: `python get_chat_id.py` (with new token in .env)
4. **Update .env with new token and chat ID**
5. **Test**: `python src/scanner.py`

## 🚨 Important Notes

- The old token is compromised and must be revoked
- Anyone with access to the git history can see the old token
- Consider the git history cleanup if this is a public repository
- Always use environment variables for sensitive data

