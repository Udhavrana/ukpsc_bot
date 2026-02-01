#!/usr/bin/env python3
"""
UKPSC Notification Bot - Render.com Version
Checks for new exam notifications and sends Telegram alerts
Optimized for continuous running on Render's free tier
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import asyncio
from telegram import Bot
from telegram.error import TelegramError

# ============================================
# CONFIGURATION - Uses Environment Variables
# ============================================
TELEGRAM_BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('CHAT_ID')
# ============================================

UKPSC_URL = "https://ukpsc.gov.in"
NOTIFICATIONS_FILE = "ukpsc_seen.json"


def load_seen_notifications():
    """Load previously seen notifications"""
    if os.path.exists(NOTIFICATIONS_FILE):
        try:
            with open(NOTIFICATIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []


def save_seen_notifications(seen_list):
    """Save seen notifications to file"""
    with open(NOTIFICATIONS_FILE, 'w') as f:
        json.dump(seen_list, f, indent=2)


def fetch_ukpsc_notifications():
    """Scrape UKPSC website for new notifications"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching UKPSC notifications...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(UKPSC_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        notifications = []
        
        # Find notification/advertisement sections
        # Try multiple selectors to catch different page structures
        selectors = [
            'div.notification',
            'div.latest-news',
            'div.advertisement',
            'table.table',
            'div.news-section',
            'ul.notification-list',
            'div.content-section'
        ]
        
        notification_containers = []
        for selector in selectors:
            containers = soup.select(selector)
            if containers:
                notification_containers.extend(containers)
                break
        
        # If no specific containers found, search all links
        if not notification_containers:
            notification_containers = [soup]
        
        # Extract notifications
        for container in notification_containers:
            links = container.find_all('a', href=True)
            
            for link in links[:30]:  # Limit to first 30 links
                try:
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    # Skip empty or very short titles
                    if not title or len(title) < 15:
                        continue
                    
                    # Make absolute URL
                    if href and not href.startswith('http'):
                        href = UKPSC_URL + ('/' if not href.startswith('/') else '') + href
                    
                    # Filter exam-related content (expanded keywords)
                    exam_keywords = [
                        'exam', 'recruitment', 'notification', 'advertisement',
                        'bharti', 'advt', 'post', 'vacancy', 'परीक्षा',
                        'interview', 'result', 'admit', 'answer key',
                        'application', 'selection', 'combined', 'pcs',
                        'assistant', 'officer', 'lecturer', 'teacher'
                    ]
                    
                    title_lower = title.lower()
                    if any(kw in title_lower for kw in exam_keywords):
                        # Try to find date
                        date_text = "Date not available"
                        parent = link.find_parent()
                        if parent:
                            import re
                            text = parent.get_text()
                            date_match = re.search(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', text)
                            if date_match:
                                date_text = date_match.group()
                        
                        notification = {
                            'id': f"{title[:50]}_{href[:40]}",
                            'title': title,
                            'link': href,
                            'date': date_text,
                            'found_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        notifications.append(notification)
                
                except Exception as e:
                    continue
        
        # Remove duplicates based on ID
        seen_ids = set()
        unique_notifications = []
        for notif in notifications:
            if notif['id'] not in seen_ids:
                seen_ids.add(notif['id'])
                unique_notifications.append(notif)
        
        print(f"Found {len(unique_notifications)} notifications on the page")
        return unique_notifications
    
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        return []


def extract_details_from_page(url):
    """Extract detailed information from notification page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get all text
        text = soup.get_text(separator=' ', strip=True)
        
        # Extract key information
        import re
        
        details = {}
        
        # Application dates
        app_start_patterns = [
            r'(?:application|online)\s+(?:start|from)[:\s]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
            r'(?:start|from)[:\s]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})'
        ]
        for pattern in app_start_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['app_start'] = match.group(1)
                break
        
        # Last date
        last_date_patterns = [
            r'(?:last|closing|end)\s+date[:\s]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
            r'(?:till|upto|until)[:\s]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})'
        ]
        for pattern in last_date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['last_date'] = match.group(1)
                break
        
        # Exam date
        exam_patterns = [
            r'exam(?:ination)?\s+date[:\s]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
            r'परीक्षा\s+तिथि[:\s]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})'
        ]
        for pattern in exam_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['exam_date'] = match.group(1)
                break
        
        # Fee
        fee_pattern = r'(?:fee|शुल्क)[:\s]+(?:rs\.?|₹)?\s*([0-9,]+)'
        match = re.search(fee_pattern, text, re.IGNORECASE)
        if match:
            details['fee'] = f"₹{match.group(1)}"
        
        return details
    
    except Exception as e:
        print(f"Error extracting details: {e}")
        return {}


async def send_telegram_notification(bot, chat_id, notification, details):
    """Send formatted notification via Telegram"""
    try:
        message = f"🔔 <b>New UKPSC Notification!</b>\n\n"
        message += f"📋 <b>{notification['title']}</b>\n\n"
        
        if notification.get('date') and notification['date'] != "Date not available":
            message += f"📅 <b>Posted:</b> {notification['date']}\n\n"
        
        if details.get('app_start'):
            message += f"🟢 <b>Application Start:</b> {details['app_start']}\n"
        
        if details.get('last_date'):
            message += f"🔴 <b>Last Date:</b> {details['last_date']}\n"
        
        if details.get('exam_date'):
            message += f"📝 <b>Exam Date:</b> {details['exam_date']}\n"
        
        if details.get('fee'):
            message += f"💰 <b>Fee:</b> {details['fee']}\n"
        
        message += f"\n🔗 <a href='{notification['link']}'>Click here for full details</a>\n"
        message += f"\n⏰ <i>Checked at: {notification['found_at']}</i>"
        
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=False
        )
        
        print(f"✓ Sent: {notification['title'][:60]}...")
        return True
    
    except TelegramError as e:
        print(f"✗ Telegram error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error sending message: {e}")
        return False


async def main():
    """Main execution function"""
    print("=" * 70)
    print("UKPSC Notification Bot - Render.com Version")
    print(f"Run started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Validate configuration
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("\n⚠️  ERROR: Environment variables not set!")
        print("\nPlease set these in Render dashboard:")
        print("  BOT_TOKEN = your bot token from BotFather")
        print("  CHAT_ID = your chat ID from userinfobot")
        return
    
    # Initialize bot
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Load seen notifications
    seen_notifications = load_seen_notifications()
    print(f"Loaded {len(seen_notifications)} previously seen notifications")
    
    # Fetch current notifications
    all_notifications = fetch_ukpsc_notifications()
    
    # Filter for new notifications only
    new_notifications = [
        n for n in all_notifications 
        if n['id'] not in seen_notifications
    ]
    
    print(f"Found {len(new_notifications)} NEW notifications")
    
    # Send notifications
    if new_notifications:
        for notification in new_notifications:
            # Get detailed info
            details = extract_details_from_page(notification['link'])
            
            # Send to Telegram
            success = await send_telegram_notification(bot, TELEGRAM_CHAT_ID, notification, details)
            
            if success:
                # Mark as seen
                seen_notifications.append(notification['id'])
                
                # Wait between messages to avoid rate limiting
                await asyncio.sleep(2)
        
        # Save updated seen list
        save_seen_notifications(seen_notifications)
        print(f"\n✅ Sent {len(new_notifications)} notification(s)")
    else:
        print("✅ No new notifications (all previously seen)")
    
    print("=" * 70)
    print(f"Run completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
