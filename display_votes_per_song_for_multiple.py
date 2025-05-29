import os, io, json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

SERVICE_ACCOUNT_FILE = "/root/.config/service_account.json"
INPUT_FOLDER_ID = "1_vr56jMd4aQaahI_bUvSRYcdxyGHY8zG"     # reduced_votes
OUTPUT_FOLDER_ID = "16AdOIvSlwUHAcVqiulWovp1WaeUHiuJ"     # display_votes
FILE_NAME = "reduced_votes.json"
LOCAL_FILE = "/app/reduced_votes.json"
OUTPUT_FILE = "display_votes.json"

# Auth
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
service = build("drive", "v3", credentials=creds)

# Zoek meest recent bestand
response = service.files().list(
    q=f"name='{FILE_NAME}' and '{INPUT_FOLDER_ID}' in parents",
    spaces="drive",
    fields="files(id, name, modifiedTime)",
    orderBy="modifiedTime desc"
).execute()

files = response.get("files", [])
if not files:
    raise Exception("❌ reduced_votes.json niet gevonden.")

file_id = files[0]["id"]
print(f"📥 Gekozen bestand ID: {file_id}, laatst gewijzigd: {files[0]['modifiedTime']}")

# Download
request = service.files().get_media(fileId=file_id)
with open(LOCAL_FILE, "wb") as f:
    downloader = MediaIoBaseDownload(f, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

if os.path.getsize(LOCAL_FILE) == 0:
    raise Exception("❌ Bestand is leeg.")

# Verwerk data
try:
    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        raise Exception("⚠️ JSON bevat geen data.")

    print("🎶 Vote Summary per Country:\n")
    for entry in data:
        country = entry.get("country", "Unknown")
        print(f"🌍 Country: {country}")
        for vote in entry.get("votes", []):
            print(f"  🎵 Song {vote['song_number']}: {vote['count']} votes")
        print()

    # 🔽 Schrijf output lokaal weg als display_votes.json
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(data, out, indent=2)

    # 🔼 Upload naar display_votes-map
    metadata = {
        "name": OUTPUT_FILE,
        "parents": [OUTPUT_FOLDER_ID]
    }
    media = MediaFileUpload(OUTPUT_FILE, mimetype="application/json")
    upload = service.files().create(body=metadata, media_body=media, fields="id").execute()
    print(f"✅ Bestand geüpload naar display_votes map. Bestand-ID: {upload['id']}")

except json.JSONDecodeError:
    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        print("⚠️ JSON Decode Error. Inhoud bestand:")
        print(f.read())
    raise

except Exception as e:
    print(f"🚫 Fout: {e}")
