import urllib.request
import os

def download_audio():
    # URL to download English female speech "Yeah, right there daddy... ohhh"
    url = "https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q=Yeah%20right%20there%20daddy...%20ohhh"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    web_dir = os.path.join("web")
    app_dir = os.path.join("app")
    
    os.makedirs(web_dir, exist_ok=True)
    os.makedirs(app_dir, exist_ok=True)
    
    req = urllib.request.Request(url, headers=headers)
    print("Downloading default audio file from Google Translate TTS...")
    
    try:
        with urllib.request.urlopen(req) as response:
            data = response.read()
            
            # Save to web folder
            with open(os.path.join(web_dir, "daddy.mp3"), "wb") as f:
                f.write(data)
                
            # Save to app folder
            with open(os.path.join(app_dir, "daddy.mp3"), "wb") as f:
                f.write(data)
                
        print("Success! Audio saved as 'daddy.mp3' in both web and app directories.")
    except Exception as e:
        print(f"Error downloading audio: {e}")

if __name__ == "__main__":
    download_audio()
