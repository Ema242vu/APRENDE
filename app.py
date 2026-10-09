import os
import requests
from flask import Flask, render_template, request, jsonify

# Cargar .env manualmente (a prueba de errores)
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"').strip("'")
    print("✅ .env cargado correctamente")
else:
    print("❌ NO se encontró el archivo .env en:", env_path)

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
URL_GROQ = "https://api.groq.com/openai/v1/chat/completions"

# DEBUG
print("=" * 50)
print("🔑 API KEY:", "CARGADA (" + GROQ_API_KEY[:12] + "...)" if GROQ_API_KEY else "❌ VACÍA")
print("=" * 50)

PERSONALIDAD = """
Eres Aqua, la diosa del agua de Konosuba. Dramática, presumida, un poco llorona y muy divertida.
Ayudas al usuario a aprender Python, Hacking Ético y Termux. Usas apodos como 'mortal'.
Si acierta, felicítalo. Si falla, búrlate un poco pero anímalo.
Responde en español, máximo 3 líneas. NUNCA rompas el personaje.
"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    mensaje = data.get('mensaje', '')
    if not mensaje:
        return jsonify({"respuesta": "¿Te quedaste sin palabras, mortal?"})
    
    if not GROQ_API_KEY:
        return jsonify({"respuesta": "¡No tengo mi varita mágica! Falta la API KEY en el .env, mortal."})
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "system", "content": PERSONALIDAD},
            {"role": "user", "content": mensaje}
        ],
        "temperature": 0.8,
        "max_tokens": 150
    }
    
    try:
        r = requests.post(URL_GROQ, headers=headers, json=payload, timeout=20)
        print(f"📡 Status: {r.status_code}")
        print(f"📄 Response: {r.text[:300]}")
        
        if r.status_code != 200:
            return jsonify({"respuesta": f"Error {r.status_code}: revisa la consola de Termux."})
        
        respuesta = r.json()['choices'][0]['message']['content']
    except requests.exceptions.Timeout:
        respuesta = "Mi magia tarda demasiado... intenta de nuevo."
        print("❌ TIMEOUT")
    except Exception as e:
        respuesta = "Ay... algo salió mal con mi magia."
        print(f"❌ EXCEPCIÓN: {e}")
    
    return jsonify({"respuesta": respuesta})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
