import azure.functions as func
from azure.storage.blob import BlobServiceClient
import azure.cognitiveservices.speech as speechsdk
import os

speech_key = os.getenv("AZURE_SPEECH_KEY")
speech_region = os.getenv("AZURE_SPEECH_REGION")
storage_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

def transcribe_audio(blob_url):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    audio_config = speechsdk.audio.AudioConfig(filename=blob_url)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = recognizer.recognize_once()
    return result.text if result.reason == speechsdk.ResultReason.RecognizedSpeech else "Transcription failed"

def main(req: func.HttpRequest) -> func.HttpResponse:
    req_body = req.get_json()
    blob_name = req_body.get('file_name')

    if not blob_name:
        return func.HttpResponse("Invalid request, must include 'file_name'", status_code=400)

    blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
    blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/audio-files/{blob_name}"

    transcript = transcribe_audio(blob_url)
    return func.HttpResponse(transcript, status_code=200)
