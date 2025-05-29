import json

# Define the path to the output file
input_file = "reduced_votes.json"

try:
    # Open and load the JSON data
    with open(input_file, "r") as f:
        data = json.load(f)

    # Display the data in a readable format
    print("Vote Summary per Country:\n")
    for entry in data:
        country = entry["country"]
        print(f"Country: {country}")
        for vote in entry["votes"]:
            print(f"  Song {vote['song_number']}: {vote['count']} votes")
        print()  # empty line between countries

except FileNotFoundError:
    print(f"File '{input_file}' not found.")
except json.JSONDecodeError:
    print(f"Error decoding JSON from '{input_file}'.")
