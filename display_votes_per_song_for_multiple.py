import os, io, json
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

SERVICE_ACCOUNT_FILE = "/root/.config/service_account.json"
INPUT_FOLDER_ID = "1_vr56jMd4aQaahI_bUvSRYcdxyGHY8zG"     # map met reduced_votes_se.txt
OUTPUT_FOLDER_ID = "16AdOIvSlwUHAcVqIiulWovp1WaeUHiuJ"    # map waar display_votes.json naartoe gaat
FILE_NAME = "reduced_votes.json"
LOCAL_FILE = "/app/reduced_votes_se.txt"
OUTPUT_FILE = "display_votes.json"

# === Authenticate ===
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
service = build("drive", "v3", credentials=creds)

# Zoek alle bestanden met de juiste naam en folder
response = service.files().list(
    q=f"name='{FILE_NAME}' and '{INPUT_FOLDER_ID}' in parents",
    spaces="drive",
    fields="files(id, name, modifiedTime)",
    orderBy="modifiedTime desc"
).execute()

files = response.get("files", [])
if not files:
    raise Exception("❌ Geen bestand gevonden met de naam reduced_votes.json in de map.")

# Neem het meest recente bestand
file_id = files[0]["id"]

print(f"📄 Gekozen bestand: {files[0]['name']} (laatst gewijzigd: {files[0]['modifiedTime']})")


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
    print(f"Error decoding JSON from '{LOCAL_FILE}'.")

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
