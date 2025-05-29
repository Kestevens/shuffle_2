import os, io, json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SERVICE_ACCOUNT_FILE = "/root/.config/service_account.json"
INPUT_FOLDER_ID = "1_vr56jMd4aQaahI_bUvSRYcdxyGHY8zG"
FILE_NAME = "reduced_votes.json"
LOCAL_FILE = "/app/reduced_votes.json"

# Authenticatie
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
service = build("drive", "v3", credentials=creds)

# Zoek het meest recente bestand met juiste naam in juiste map
response = service.files().list(
    q=f"name='{FILE_NAME}' and '{INPUT_FOLDER_ID}' in parents",
    spaces="drive",
    fields="files(id, name, modifiedTime)",
    orderBy="modifiedTime desc"
).execute()

files = response.get("files", [])
if not files:
    raise Exception("❌ Bestand niet gevonden in reduced_votes-map.")

file_id = files[0]["id"]
print(f"📥 Gekozen bestand ID: {file_id}, laatst gewijzigd: {files[0]['modifiedTime']}")

# Download bestand
request = service.files().get_media(fileId=file_id)
with open(LOCAL_FILE, "wb") as f:
    downloader = MediaIoBaseDownload(f, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

# Controleer bestandsgrootte
file_size = os.path.getsize(LOCAL_FILE)
print(f"📦 Bestandsgrootte: {file_size} bytes")

if file_size == 0:
    raise Exception("❌ Gedownload bestand is leeg.")

# Probeer JSON in te lezen
try:
    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        raise Exception("⚠️ JSON is geldig maar bevat geen data.")

    print("🎶 Vote Summary per Country:\n")
    for entry in data:
        country = entry.get("country", "Unknown")
        print(f"🌍 Country: {country}")
        for vote in entry.get("votes", []):
            print(f"  🎵 Song {vote['song_number']}: {vote['count']} votes")
        print()

except json.JSONDecodeError:
    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        print("⚠️ Kon JSON niet decoderen. Inhoud bestand:")
        print(f.read())
    raise Exception("❌ Ongeldige JSON in bestand.")

except Exception as e:
    print(f"🚫 Fout: {e}")
