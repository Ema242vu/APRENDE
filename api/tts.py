import os
import json
import requests
from http.server import BaseHTTPRequestHandler

ELEVENLABS_URL = "https://api.elevenlabs.io/v1/text-to-speech"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            data = json.loads(body) if body else {}
            texto = data.get('texto', '')
            voice_id = data.get('voice_id', 'xYrwTY3IRh6VBodoZUNN')
            model_id = data.get('model_id', 'eleven_multilingual_v2')

            api_key = os.environ.get('ELEVENLABS_API_KEY', '')

            if not texto or not api_key:
                self._responder({"error": "Falta texto o API Key"}, 400)
                return

            headers = {
                "xi-api-key": api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "text": texto,
                "model_id": model_id,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.3,
                    "use_speaker_boost": True
                }
            }

            response = requests.post(
                f"{ELEVENLABS_URL}/{voice_id}",
                headers=headers,
                json=payload,
                timeout=20
            )

            if response.status_code == 200:
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mpeg')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.content)
            else:
                self._responder({"error": f"ElevenLabs: {response.status_code} - {response.text[:200]}"}, 500)
        except Exception as e:
            self._responder({"error": f"Error: {str(e)[:80]}"}, 500)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _responder(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
