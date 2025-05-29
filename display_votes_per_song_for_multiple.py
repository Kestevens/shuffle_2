import os, io, json
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

SERVICE_ACCOUNT_FILE = "/root/.config/service_account.json"
INPUT_FOLDER_ID = "1_vr56jMd4aQaahI_bUvSRYcdxyGHY8zG"     # map met reduced_votes_se.txt
OUTPUT_FOLDER_ID = "16AdOIvSlwUHAcVqIiulWovp1WaeUHiuJ"    # map waar display_votes.json naartoe gaat
FILE_NAME = "reduced_votes_se.txt"
LOCAL_FILE = "/app/reduced_votes_se.txt"
OUTPUT_FILE = "display_votes.json"

# === Authenticate ===
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
service = build("drive", "v3", credentials=creds)

# === Download bestand van Google Drive ===
response = service.files().list(
    q=f"name='{FILE_NAME}' and '{INPUT_FOLDER_ID}' in parents",
    spaces="drive",
    fields="files(id, name)"
).execute()

files = response.get("files", [])
if not files:
    raise Exception("❌ Bestand niet gevonden in reduced_votes-map.")
file_id = files[0]["id"]

request = service.files().get_media(fileId=file_id)
fh = open(LOCAL_FILE, "wb")
downloader = MediaIoBaseDownload(fh, request)
done = False
while not done:
    status, done = downloader.next_chunk()
print("📥 Bestand gedownload uit reduced_votes.")

# === Verwerk JSON-bestand ===
try:
    with open(LOCAL_FILE, "r") as f:
        data = json.load(f)

    # Display the data in a readable format
    print("Vote Summary per Country:\n")
    for entry in data:
        country = entry["country"]
        print(f"Country: {country}")
        for vote in entry["votes"]:
            print(f"  Song {vote['song_number']}: {vote['count']} votes")
        print()  # empty line between countries

# Sla JSON opnieuw op (voor upload)
    with open(OUTPUT_FILE, "w") as f_out:
        json.dump(data, f_out, indent=2)

except FileNotFoundError:
    print(f"File '{input_file}' not found.")
except json.JSONDecodeError:
    print(f"Error decoding JSON from '{input_file}'.")

# Upload naar Drive
file_metadata = {
    "name": OUTPUT_FILE,
    "parents": [OUTPUT_FOLDER_ID]
}
media = MediaFileUpload(OUTPUT_FILE, mimetype="application/json")
uploaded_file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields="id"
).execute()
print(f"✅ Bestand geüpload naar 'display_votes' map. Bestand-ID: {uploaded_file['id']}")
