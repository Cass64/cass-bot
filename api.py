from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

# ✅ Route d'accueil (toujours renvoyer du JSON)
@app.route('/')
def home():
    return jsonify({'message': 'API Discord-Bot en ligne ! 🚀'})

# 🚀 Démarrer le bot
@app.route('/start-bot', methods=['POST'])
def start_bot():
    try:
        subprocess.Popen(['python', 'start.py'])
        return jsonify({'status': 'Bot démarré avec succès !'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 💬 Envoyer un message à un canal Discord
@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    message = data.get('message')
    channel_id = data.get('channel_id')

    if not message or not channel_id:
        return jsonify({'error': 'Message et channel_id requis'}), 400

    try:
        subprocess.run(['python', 'client.py', channel_id, message])
        return jsonify({'status': 'Message envoyé avec succès !'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))  # Port défini par Render
    app.run(host='0.0.0.0', port=port)
