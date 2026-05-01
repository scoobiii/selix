import os
from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", "SUA_CHAVE_AQUI"))

model = genai.GenerativeModel("gemini-1.5-flash")
app = Flask(__name__, static_folder=".")

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    pergunta = request.json.get("pergunta", "")
    prompt = f"Você é assistente do projeto SELIX. Responda com base nos dados: Selic ideal 9,25%, juro real 4,77%, Investment Grade BBB+. Pergunta: {pergunta}"
    resposta = model.generate_content(prompt).text
    return jsonify({"resposta": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
