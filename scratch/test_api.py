import json
import requests
import os

def test_get_stories():
    # 1. Local Stories
    try:
        with open('stories.json', 'r') as f:
            stories = json.load(f)
        print(f"Loaded {len(stories)} local stories.")
    except Exception as e:
        print(f"Local Stories Error: {e}")
        stories = {}

    # 2. Public API - Gutendex (Mystery Topic)
    GUTENBERG_API = "https://gutendex.com/books/?topic=mystery"
    try:
        print(f"Fetching from API: {GUTENBERG_API}")
        response = requests.get(GUTENBERG_API, timeout=10)
        print(f"API Response Status: {response.status_code}")
        if response.status_code == 200:
            books = response.json().get('results', [])[:6]
            print(f"Found {len(books)} books from API.")
            for book in books:
                b_id = f"api_{book['id']}"
                stories[b_id] = {
                    "title": f"[ARCHIVE] {book['title']}",
                    "is_api": True,
                    "start": {
                        "text": f"You discover an ancient digital manuscript. Author: {book['authors'][0]['name'] if book['authors'] else 'Unknown'}. This is a read-only historical archive.",
                        "choices": [] 
                    }
                }
        else:
            print(f"API failed with status {response.status_code}")
    except Exception as e:
        print(f"API Fetch Error: {e}")
    
    print(f"Total stories: {len(stories)}")
    for s_id, s in stories.items():
        print(f"- {s_id}: {s.get('title')}")

if __name__ == "__main__":
    test_get_stories()
