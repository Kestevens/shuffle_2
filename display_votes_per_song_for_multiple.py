import os, io, json
import pandas as pd
from collections import defaultdict
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

SERVICE_ACCOUNT_FILE = "/root/.config/service_account.json"
INPUT_FOLDER_ID = "1EYf9den2D8IVAGvVDrH1ACp6C89z7p1f"
OUTPUT_FOLDER_ID = "16AdOIvSlwUHAcVqIiulWovp1WaeUHiuJ"
FILE_NAME = "generated_votes.txt"
LOCAL_FILE = "/app/generated_votes.txt"
OUTPUT_FILE = "display_votes.json"

# === Google Drive authenticatie ===
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
service = build("drive", "v3", credentials=creds)

# === Meest recente bestand ophalen ===
response = service.files().list(
    q=f"name='{FILE_NAME}' and '{INPUT_FOLDER_ID}' in parents",
    spaces="drive",
    fields="files(id, name, modifiedTime)",
    orderBy="modifiedTime desc"
).execute()

files = response.get("files", [])
if not files:
    raise Exception("❌ generated_votes.txt niet gevonden op Drive.")

file_id = files[0]["id"]
print(f"📥 Gekozen bestand ID: {file_id}, laatst gewijzigd: {files[0]['modifiedTime']}")

# === Download bestand ===
request = service.files().get_media(fileId=file_id)
with open(LOCAL_FILE, "wb") as f:
    downloader = MediaIoBaseDownload(f, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

# === Verwerk stemdata ===
try:
    df = pd.read_csv(LOCAL_FILE, sep="\t")

    if "COUNTRY CODE" not in df.columns or "SONG NUMBER" not in df.columns:
        raise Exception("❌ Kolommen 'COUNTRY CODE' of 'SONG NUMBER' ontbreken.")

    # Stemmen tellen per land en per song
    result = defaultdict(dict)

    grouped = df.groupby(["COUNTRY CODE", "SONG NUMBER"]).size().reset_index(name="votes")
    for _, row in grouped.iterrows():
        country = row["COUNTRY CODE"]
        song = str(row["SONG NUMBER"])
        votes = int(row["votes"])
        result[country][song] = votes

    # Print op het scherm
    print("\n🎵 Vote Summary per Country:\n")
    for country, votes in result.items():
        print(f"Country: {country}")
        for song, count in sorted(votes.items(), key=lambda x: x[1], reverse=True):
            print(f"  Song {song}: {count} votes")
        print()

    # === Upload JSON-output naar Drive ===
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    metadata = {
        "name": OUTPUT_FILE,
        "parents": [OUTPUT_FOLDER_ID]
    }
    media = MediaFileUpload(OUTPUT_FILE, mimetype="application/json")
    uploaded = service.files().create(body=metadata, media_body=media, fields="id").execute()

    print(f"✅ Bestand geüpload naar display_votes map. Bestand-ID: {uploaded['id']}")

except Exception as e:
    print(f"🚫 Fout bij verwerking: {e}")
