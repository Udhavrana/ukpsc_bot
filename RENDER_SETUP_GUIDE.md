# UKPSC Bot Deployment on Render.com - Complete Free Guide

## 🎯 What You'll Get
- ✅ Completely FREE hosting
- ✅ Runs 24/7 automatically
- ✅ No website restrictions
- ✅ Automatic restarts if it crashes
- ✅ Easy deployment from GitHub

---

## 📋 PART 1: Prepare Your Telegram Bot (Skip if Already Done)

### If you already created your bot with BotFather - SKIP THIS
### If not, do this:

1. Open Telegram → Search **@BotFather**
2. Send `/newbot`
3. Name: `UKPSC Notification Bot`
4. Username: `ukpsc_notify_yourname_bot`
5. **Copy the token** (looks like: `1234567890:ABC...`)
6. Search **@userinfobot** → Get your Chat ID
7. Search for your bot → Click START

**Save these:**
- Bot Token: `________________`
- Chat ID: `________________`

---

## 📋 PART 2: Create GitHub Account (Free)

We need GitHub to store your code, then Render will deploy it from there.

### Step 1: Sign Up
1. Go to: **https://github.com/signup**
2. Enter your email
3. Create a password
4. Choose a username
5. Verify your email
6. Click "Skip personalization" (or answer questions)

### Step 2: You're Done!
You now have a GitHub account.

---

## 📋 PART 3: Upload Your Bot to GitHub

### Step 1: Create New Repository
1. Go to: **https://github.com/new**
2. Repository name: `ukpsc-telegram-bot`
3. Description: `UKPSC exam notification bot`
4. Select: **Public** (must be public for free Render)
5. ✅ Check "Add a README file"
6. Click **"Create repository"**

### Step 2: Upload Bot Files
Now you'll upload 3 files:

**FILE 1: requirements.txt**
1. Click **"Add file"** → **"Create new file"**
2. Name: `requirements.txt`
3. Paste this content:
   ```
   requests>=2.31.0
   beautifulsoup4>=4.12.0
   python-telegram-bot>=20.0
   lxml>=4.9.0
   ```
4. Click **"Commit changes"** (green button at bottom)

**FILE 2: ukpsc_bot.py**
1. Click **"Add file"** → **"Create new file"**
2. Name: `ukpsc_bot.py`
3. Copy the ENTIRE content from `ukpsc_check_once.py` file I created
4. **IMPORTANT:** Replace these lines:
   ```python
   TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
   ```
   With:
   ```python
   import os
   TELEGRAM_BOT_TOKEN = os.environ.get('BOT_TOKEN')
   TELEGRAM_CHAT_ID = os.environ.get('CHAT_ID')
   ```
5. Click **"Commit changes"**

**FILE 3: start.sh**
1. Click **"Add file"** → **"Create new file"**
2. Name: `start.sh`
3. Paste this content:
   ```bash
   #!/bin/bash
   while true; do
       python ukpsc_bot.py
       echo "Waiting 3 hours before next check..."
       sleep 10800
   done
   ```
4. Click **"Commit changes"**

### Step 3: Verify Files
Your repository should now have these 4 files:
- ✅ README.md
- ✅ requirements.txt
- ✅ ukpsc_bot.py
- ✅ start.sh

---

## 📋 PART 4: Deploy on Render.com

### Step 1: Sign Up for Render
1. Go to: **https://render.com/register**
2. Click **"Sign up with GitHub"** (easier!)
3. Authorize Render to access your GitHub
4. You're logged in!

### Step 2: Create New Web Service
1. Click **"New +"** (top right)
2. Select **"Background Worker"** (NOT Web Service!)
3. Click **"Connect a repository"**
4. Find `ukpsc-telegram-bot` in the list
5. Click **"Connect"**

### Step 3: Configure the Service
Fill in these details:

**Name:** `ukpsc-bot` (or anything you like)

**Region:** Choose closest to India (Singapore or Frankfurt)

**Branch:** `main`

**Runtime:** `Python 3`

**Build Command:** 
```
pip install -r requirements.txt
```

**Start Command:**
```
bash start.sh
```

### Step 4: Add Environment Variables (SECRET VALUES)
Scroll down to **"Environment Variables"** section:

1. Click **"Add Environment Variable"**
2. Key: `BOT_TOKEN`
   Value: [Paste your bot token here]

3. Click **"Add Environment Variable"** again
4. Key: `CHAT_ID`
   Value: [Paste your chat ID here]

### Step 5: Choose Free Plan
Scroll down to **"Instance Type"**
- Select: **"Free"** (0$/month)

### Step 6: Deploy!
Click **"Create Background Worker"** at the bottom

---

## 📋 PART 5: Watch It Deploy

### Step 1: Deployment Progress
You'll see a deployment log. Wait for:
```
==> Installing dependencies...
==> Build successful!
==> Starting service...
```

This takes 2-3 minutes.

### Step 2: Check Your Telegram!
Within a few minutes, you should receive messages from your bot!

### Step 3: View Logs
Click **"Logs"** tab to see what's happening:
```
UKPSC Notification Bot - Single Check
Run started: 2026-02-01 10:30:45
Fetching UKPSC notifications...
Found X notifications
```

---

## 🎉 SUCCESS! Your Bot is Running!

### What's Happening Now:
1. ✅ Bot runs on Render's servers (FREE)
2. ✅ Checks UKPSC every 3 hours
3. ✅ Sends you Telegram notifications
4. ✅ Runs 24/7 automatically
5. ✅ Auto-restarts if it crashes

---

## ⚙️ CUSTOMIZATION

### Change Check Frequency
Edit `start.sh` in GitHub:

**Every 1 hour:**
```bash
sleep 3600
```

**Every 6 hours:**
```bash
sleep 21600
```

**Every 12 hours:**
```bash
sleep 43200
```

After editing, Render will auto-redeploy!

### View Logs Anytime
- Go to Render dashboard
- Click your service
- Click "Logs" tab
- See real-time activity

---

## 🔧 TROUBLESHOOTING

### Bot not sending messages?
1. Check Render logs for errors
2. Verify environment variables (BOT_TOKEN and CHAT_ID)
3. Make sure you clicked START on your bot in Telegram

### "Build failed" error?
- Check that `requirements.txt` is spelled correctly
- Make sure all files are in the root (not in a folder)

### Want to manually trigger a check?
1. Go to Render dashboard
2. Click your service
3. Click "Manual Deploy" → "Deploy latest commit"

### Bot stopped working?
- Render free tier sleeps after 15 minutes of inactivity
- Use the `start.sh` loop to keep it running
- Check logs for any errors

---

## 📊 MONITORING

### Check if Bot is Running
1. Render Dashboard → Your service
2. Status should show: **"Live"** (green)
3. Check "Logs" for recent activity

### Get Notified of Issues
Render sends email if your service crashes

---

## 💡 TIPS

1. **Keep GitHub repo updated** - Any changes you push will auto-deploy
2. **Monitor Telegram** - You'll get notifications when exams are posted
3. **Check logs occasionally** - Make sure bot is running smoothly
4. **Free tier limits** - Render free tier gives 750 hours/month (plenty!)

---

## 🚀 YOU'RE ALL SET!

Your UKPSC notification bot is now:
- ✅ Running in the cloud (FREE)
- ✅ Checking every 3 hours
- ✅ Sending detailed Telegram alerts
- ✅ Working 24/7 automatically

**Next time UKPSC posts an exam notification, you'll be the first to know!** 📱

---

## 🆘 NEED HELP?

Check Render logs first - they show exactly what's happening. Common issues:
- Wrong environment variables → Update in Render settings
- Bot token expired → Get new one from BotFather
- Service stopped → Click "Manual Deploy" to restart

**Happy exam hunting!** 🎓
