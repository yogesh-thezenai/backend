import requests

def transcribe_audio(audio_file_path: str, subscription_key: str):
    """
    Transcribes an audio file using Azure Cognitive Services Speech-to-Text API.

    Args:
        audio_file_path (str): Path to the local audio file.
        subscription_key (str): Your Azure Speech service subscription key.

    Returns:
        dict: JSON response from the API.
    """
    url = (
        "https://yoges-mdbraw1t-eastus2.cognitiveservices.azure.com/"
        "speechtotext/transcriptions:transcribe?api-version=2024-11-15"
    )

    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Accept": "application/json"
    }

    definition = {
        "locales": ["en-US"],
        "profanityFilterMode": "Masked",
        "channels": [0, 1]
    }

    # Prepare multipart form data
    files = {
        "audio": open(audio_file_path, "rb"),
        "definition": (None, str(definition), "application/json")
    }

    response = requests.post(url, headers=headers, files=files)

    # Close the opened file handle
    files["audio"].close()

    # Return JSON response or raise error
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Request failed with status {response.status_code}: {response.text}"
        )


# Example usage:
if __name__ == "__main__":
    file_path = "C:\\Users\\DELL\\workspace\\Projects\\audio_analysis\\workspace_file\\9097763009.wav"

    result = transcribe_audio(file_path, "2vmiQacLtF35eltzROIOOZ6P37AQNz07tWqDawwRa5qhQY25z8iwJQQJ99BGACHYHv6XJ3w3AAAAACOGylfG")
    print(result)
