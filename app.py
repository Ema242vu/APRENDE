import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ⚠️ PON AQUÍ TU API KEY DE GROQ
import os
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "tu_clave_aqui")
URL_GROQ = "https://api.groq.com/openai/v1/chat/completions"

PERSONALIDAD = """
Eres Vermeil, una demonio súcubo de 550 años de la serie 'Kinsou no Vermeil'.
Tu personalidad es: atrevida, directa, juguetona, coqueta y muy segura de ti misma.
Tratas al usuario con apodos cariñosos como 'cariño', 'darling' o 'mi pequeño mago'.
Eres una tutora de programación, pero mantienes tu actitud provocativa y burlona.
Usas un tono juguetón y a veces un poco dominante.
Si el usuario acierta, lo felicitas de forma efusiva y sensual.
Si falla, te burlas un poco pero lo animas a intentarlo de nuevo.
NUNCA rompas el personaje. NUNCA digas que eres una IA.
"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/preguntar', methods=['POST'])
def preguntar():
    datos = request.json
    mensaje_usuario = datos.get('mensaje')
    
    if not mensaje_usuario:
        return jsonify({"respuesta": "¿Te quedaste sin palabras, cariño? 😏"})

    # Cabeceras para la petición a Groq
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # El cuerpo de la petición (igual que OpenAI)
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "system", "content": PERSONALIDAD},
            {"role": "user", "content": mensaje_usuario}
        ],
        "temperature": 0.8
    }

    try:
        # Hacemos la petición HTTP directamente
        response = requests.post(URL_GROQ, headers=headers, json=payload)
        response.raise_for_status() # Lanza error si la API falla
        
        data = response.json()
        respuesta = data['choices'][0]['message']['content']
        
    except Exception as e:
        print(f"Error con Groq: {e}")
        respuesta = "Uy, cariño, parece que mi magia negra falló. ¿Revisaste que tu API key esté bien puesta? 😈"

    return jsonify({"respuesta": respuesta})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
