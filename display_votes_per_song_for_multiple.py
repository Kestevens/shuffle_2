import os, io, json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

SERVICE_ACCOUNT_FILE = "/root/.config/service_account.json"
INPUT_FOLDER_ID = "1_vr56jMd4aQaahI_bUvSRYcdxyGHY8zG"     # reduced_votes
OUTPUT_FOLDER_ID = "16AdOIvSlwUHAcVqIiulWovp1WaeUHiuJ"    # display_votes
FILE_NAME = "reduced_votes.json"
LOCAL_FILE = "/app/reduced_votes.json"
OUTPUT_FILE = "display_votes.json"

# Authenticate
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
service = build("drive", "v3", credentials=creds)

# Zoek meest recente bestand in map
response = service.files().list(
    q=f"name='{FILE_NAME}' and '{INPUT_FOLDER_ID}' in parents",
    spaces="drive",
    fields="files(id, name, modifiedTime)",
    orderBy="modifiedTime desc"
).execute()

files = response.get("files", [])
if not files:
    raise Exception("❌ reduced_votes.json niet gevonden op Drive.")

file_id = files[0]["id"]
print(f"📥 Gekozen bestand ID: {file_id}, laatst gewijzigd: {files[0]['modifiedTime']}")

# Download bestand
request = service.files().get_media(fileId=file_id)
with open(LOCAL_FILE, "wb") as f:
    downloader = MediaIoBaseDownload(f, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

# ✅ Lees en verwerk de stemdata
try:
    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        vote_data = json.load(f)

    if not isinstance(vote_data, dict):
        raise Exception("❌ Verwacht dictionary met song_number -> aantal stemmen.")

    # Sorteer op aantal stemmen (aflopend)
    sorted_votes = sorted(vote_data.items(), key=lambda x: x[1], reverse=True)

    print("\n🎵 Final Song Ranking (by total votes):\n")
    for i, (song, count) in enumerate(sorted_votes, 1):
        print(f"{i}. Song {song}: {count} votes")

    # Optional: opslaan en uploaden
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(vote_data, f, indent=2)

    metadata = {
        "name": OUTPUT_FILE,
        "parents": [OUTPUT_FOLDER_ID]
    }
    media = MediaFileUpload(OUTPUT_FILE, mimetype="application/json")
    uploaded = service.files().create(body=metadata, media_body=media, fields="id").execute()

    print(f"\n✅ Bestand geüpload naar display_votes: {uploaded['id']}")

except json.JSONDecodeError:
    print("❌ Kon JSON niet inlezen.")
except Exception as e:
    print(f"🚫 Fout: {e}")
