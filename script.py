ideoimport os
import feedparser
import requests

# ID de ta chaîne YouTube
YOUTUBE_CHANNEL_ID = "UC6UnES2h8ECK0u1K8Nq4aGA"
RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"

# Fichier pour mémoriser les vidéos déjà publiées
POSTED_FILE = "posted_videos.txt"

# REGLES : Associe des mots-clés au nom du secret GitHub correspondant
# (Modifie les mots-clés entre guillemets selon ce que tu cherches)
RULES = [
    {
        "keywords": ["dream realm", "realm"],
        "secret_name": "WEBHOOK_DREAM_REALM"
    },
    {
        "keywords": ["supreme arena", "my_supreme_arena"],
        "secret_name": "WEBHOOK_TEST_1"
    },
    {
        "keywords": ["relentless rumble", "relentless"],
        "secret_name": "WEBHOOK_TEST_2"
    }
]

def load_posted_videos():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_posted_video(video_id):
    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(f"{video_id}\n")

def main():
    posted_ids = load_posted_videos()
    feed = feedparser.parse(RSS_URL)

    # Parcourt les vidéos de la plus ancienne à la plus récente parmi les dernières publiées
    for entry in reversed(feed.entries):
        video_id = entry.yt_videoid
        if video_id in posted_ids:
            continue

        title = entry.title
        link = entry.link
        # Récupère la description depuis le flux RSS
        description = entry.summary.lower() if hasattr(entry, 'summary') else ""

        # Vérifie si un mot-clé est présent dans la description ou le titre
        for rule in RULES:
            if any(kw.lower() in description or kw.lower() in title.lower() for kw in rule["keywords"]):
                webhook_url = os.environ.get(rule["secret_name"])
                if webhook_url:
                    message = {
                        "content": f"🎥 **New video !**\n**{title}**\n{link}"
                    }
                    response = requests.post(webhook_url, json=message)
                    if response.status_code in (200, 204):
                        print(f"Vidéo {video_id} envoyée via {rule['secret_name']}.")
                        save_posted_video(video_id)
                        posted_ids.add(video_id)
                        break

if __name__ == "__main__":
    main()
