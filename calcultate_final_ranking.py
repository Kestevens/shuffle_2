import os, io, json
from collections import defaultdict
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Configuratie
SERVICE_ACCOUNT_FILE = "/root/.config/service_account.json"
INPUT_FOLDER_ID = "1_vr56jMd4aQaahI_bUvSRYcdxyGHY8zG"  # map met reduced_votes.json
FILE_NAME = "reduced_votes.json"
LOCAL_FILE = "/app/reduced_votes.json"

# Authenticate
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
service = build("drive", "v3", credentials=creds)

# Download bestand van Drive
try:
    response = service.files().list(
        q=f"name='{FILE_NAME}' and '{INPUT_FOLDER_ID}' in parents",
        spaces="drive",
        fields="files(id, name)"
    ).execute()

    files = response.get("files", [])
    if not files:
        raise FileNotFoundError(f"❌ Bestand '{FILE_NAME}' niet gevonden op Google Drive.")
    
    file_id = files[0]["id"]
    request = service.files().get_media(fileId=file_id)
    fh = open(LOCAL_FILE, "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    print("📥 reduced_votes.json succesvol gedownload.")

except Exception as e:
    print(f"Fout bij downloaden van bestand: {e}")
    exit(1)

# Verwerk stemdata
try:
    with open(LOCAL_FILE, "r") as f:
        data = json.load(f)

    total_votes = defaultdict(int)

    for entry in data:
        for vote in entry["votes"]:
            song_number = vote["song_number"]
            count = vote["count"]
            total_votes[song_number] += count

    final_ranking = sorted(total_votes.items(), key=lambda x: x[1], reverse=True)

    print("\n🎵 Final Song Ranking (by total votes):\n")
    for rank, (song, votes) in enumerate(final_ranking, start=1):
        print(f"{rank}. Song {song}: {votes} votes")

except FileNotFoundError:
    print(f"❌ Bestand '{LOCAL_FILE}' niet gevonden.")
except json.JSONDecodeError:
    print(f"❌ JSON-decodefout in '{LOCAL_FILE}'.")
except FileNotFoundError:
    print(f"File '{input_file}' not found.")
except json.JSONDecodeError:
    print(f"Error decoding JSON from '{input_file}'.")
