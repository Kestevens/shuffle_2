import json
from collections import defaultdict

# Load the JSON file
input_file = "reduced_votes.json"

try:
    with open(input_file, "r") as f:
        data = json.load(f)

    # Dictionary to store total votes per song
    total_votes = defaultdict(int)

    # Aggregate votes across all countries
    for entry in data:
        for vote in entry["votes"]:
            song_number = vote["song_number"]
            count = vote["count"]
            total_votes[song_number] += count

    # Sort songs by total votes (descending)
    final_ranking = sorted(total_votes.items(), key=lambda x: x[1], reverse=True)

    # Display the final ranking
    print("🎵 Final Song Ranking (by total votes):\n")
    for rank, (song, votes) in enumerate(final_ranking, start=1):
        print(f"{rank}. Song {song}: {votes} votes")

except FileNotFoundError:
    print(f"File '{input_file}' not found.")
except json.JSONDecodeError:
    print(f"Error decoding JSON from '{input_file}'.")
