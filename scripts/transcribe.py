#!/usr/bin/env python3
"""
Techmeme Ride Home Podcast Transcriber
自動下載並轉錄 Techmeme Ride Home Podcast
"""

import os
import json
import re
import hashlib
import feedparser
import requests
from datetime import datetime
from pathlib import Path

# Paths
PROJECT_DIR = Path(__file__).parent.parent
AUDIO_DIR = PROJECT_DIR / "audio"
DATA_DIR = PROJECT_DIR / "data"
EPISODES_FILE = DATA_DIR / "episodes.json"
PROCESSED_FILE = DATA_DIR / "processed.json"

# RSS Feed
RSS_URL = "https://feeds.megaphone.fm/ridehome"

def ensure_dirs():
    """Ensure required directories exist"""
    AUDIO_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)

def load_processed():
    """Load list of already processed episodes"""
    if PROCESSED_FILE.exists():
        return json.load(open(PROCESSED_FILE))
    return {"processed": []}

def save_processed(data):
    """Save processed episodes list"""
    json.dump(data, open(PROCESSED_FILE, 'w'), indent=2)

def load_episodes():
    """Load existing episodes"""
    if EPISODES_FILE.exists():
        return json.load(open(EPISODES_FILE))
    return {"episodes": []}

def save_episodes(data):
    """Save episodes"""
    json.dump(data, open(EPISODES_FILE, 'w'), indent=2, ensure_ascii=False)

def get_episode_id(entry):
    """Generate unique ID for an episode"""
    return hashlib.md5(entry.get('id', entry.get('link', '')).encode()).hexdigest()[:12]

def download_audio(url, filepath):
    """Download audio file"""
    print(f"Downloading: {url}")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"Saved to: {filepath}")
    return filepath

def transcribe_audio(filepath, model="base"):
    """Transcribe audio using Whisper"""
    import whisper
    
    print(f"Loading Whisper model: {model}")
    model = whisper.load_model(model)
    
    print(f"Transcribing: {filepath}")
    result = model.transcribe(str(filepath))
    
    return result["text"]

def parse_date(date_str):
    """Parse date from RSS feed"""
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str).strftime("%Y-%m-%d")
    except:
        return datetime.now().strftime("%Y-%m-%d")

def fetch_new_episodes(limit=5):
    """Fetch new episodes from RSS feed"""
    print(f"Fetching RSS: {RSS_URL}")
    feed = feedparser.parse(RSS_URL)
    
    processed = load_processed()
    new_episodes = []
    
    for entry in feed.entries[:limit]:
        episode_id = get_episode_id(entry)
        
        if episode_id in processed['processed']:
            print(f"Already processed: {entry.title}")
            continue
        
        # Find audio URL
        audio_url = None
        for link in entry.get('links', []):
            if link.get('type', '').startswith('audio/'):
                audio_url = link.get('href')
                break
        
        if not audio_url and 'enclosures' in entry:
            for enc in entry.enclosures:
                if enc.get('type', '').startswith('audio/'):
                    audio_url = enc.get('href')
                    break
        
        if not audio_url:
            print(f"No audio URL found for: {entry.title}")
            continue
        
        new_episodes.append({
            'id': episode_id,
            'title': entry.title,
            'date': parse_date(entry.get('published', '')),
            'summary': entry.get('summary', ''),
            'audio_url': audio_url,
        })
    
    return new_episodes

def process_episode(episode, whisper_model="base"):
    """Download and transcribe an episode"""
    ensure_dirs()
    
    audio_file = AUDIO_DIR / f"{episode['id']}.mp3"
    
    # Download if not exists
    if not audio_file.exists():
        download_audio(episode['audio_url'], audio_file)
    
    # Transcribe
    transcript = transcribe_audio(audio_file, model=whisper_model)
    
    # Create episode entry
    return {
        "id": episode['id'],
        "date": episode['date'],
        "title": episode['title'],
        "summary": episode['summary'][:200] + "..." if len(episode['summary']) > 200 else episode['summary'],
        "content": transcript,
        "tags": ["tech", "news"],
        "companies": []  # Will be filled by AI later
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Transcribe Techmeme Ride Home episodes")
    parser.add_argument("--limit", type=int, default=1, help="Number of episodes to process")
    parser.add_argument("--model", default="base", help="Whisper model (tiny, base, small, medium, large)")
    parser.add_argument("--list", action="store_true", help="List new episodes without processing")
    args = parser.parse_args()
    
    ensure_dirs()
    
    # Fetch new episodes
    new_episodes = fetch_new_episodes(limit=args.limit + 5)
    
    if args.list:
        print(f"\nFound {len(new_episodes)} new episodes:")
        for ep in new_episodes:
            print(f"  - [{ep['date']}] {ep['title']}")
        return
    
    if not new_episodes:
        print("No new episodes to process")
        return
    
    # Load existing data
    episodes_data = load_episodes()
    processed = load_processed()
    
    # Process episodes
    for i, episode in enumerate(new_episodes[:args.limit]):
        print(f"\n{'='*50}")
        print(f"Processing {i+1}/{args.limit}: {episode['title']}")
        print(f"{'='*50}")
        
        try:
            processed_ep = process_episode(episode, whisper_model=args.model)
            
            # Add to episodes
            episodes_data['episodes'].insert(0, processed_ep)
            
            # Mark as processed
            processed['processed'].append(episode['id'])
            
            # Save
            save_episodes(episodes_data)
            save_processed(processed)
            
            print(f"✅ Done: {episode['title']}")
            
        except Exception as e:
            print(f"❌ Error processing {episode['title']}: {e}")
    
    print(f"\n{'='*50}")
    print(f"Completed! {len(episodes_data['episodes'])} total episodes")

if __name__ == "__main__":
    main()
