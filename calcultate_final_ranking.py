import os
import io
import pandas as pd
from collections import defaultdict
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# === Configuratie ===
SERVICE_ACCOUNT_FILE = "/root/.config/service_account.json"
INPUT_FOLDER_ID = "1EYf9den2D8IVAGvVDrH1ACp6C89z7p1f"
FILE_NAME = "generated_votes.txt"
LOCAL_FILE = "/app/generated_votes.txt"

# === Authenticatie Google Drive ===
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
service = build("drive", "v3", credentials=creds)

# === Download bestand van Drive ===
try:
    response = service.files().list(
        q=f"name='{FILE_NAME}' and '{INPUT_FOLDER_ID}' in parents",
        spaces="drive",
        fields="files(id, name, modifiedTime)",
        orderBy="modifiedTime desc"
    ).execute()

    files = response.get("files", [])
    if not files:
        raise FileNotFoundError(f"❌ Bestand '{FILE_NAME}' niet gevonden op Google Drive.")
    
    file_id = files[0]["id"]
    request = service.files().get_media(fileId=file_id)
    with open(LOCAL_FILE, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
    print("📥 generated_votes.txt succesvol gedownload.")

except Exception as e:
    print(f"❌ Fout bij downloaden van bestand: {e}")
    exit(1)

# === Verwerk stemdata ===
try:
    df = pd.read_csv(LOCAL_FILE, sep="\t")

    if "SONG NUMBER" not in df.columns:
        raise ValueError("❌ Kolom 'SONG NUMBER' ontbreekt in bestand.")

    ranking = df["SONG NUMBER"].value_counts().sort_values(ascending=False)

    print("\n🎵 Final Song Ranking (by total votes):\n")
    for i, (song, votes) in enumerate(ranking.items(), start=1):
        print(f"{i}. Song {song}: {votes} votes")

except Exception as e:
    print(f"🚫 Fout tijdens verwerking: {e}")
