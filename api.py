from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'message': 'API Discord-Bot en ligne ! 🚀'})

# 🚀 Démarrer le bot
@app.route('/start-bot', methods=["GET","POST"])
def start_bot():
    try:
        print("Démarrage du bot...")  # Log pour vérifier que la route est atteinte
        subprocess.Popen(['python', 'start.py'])
        print("Bot démarré avec succès")  # Log pour confirmer que le bot a démarré
        return jsonify({'status': 'Bot démarré avec succès !'}), 200
    except Exception as e:
        print(f"Erreur lors du démarrage du bot : {str(e)}")  # Log d'erreur
        return jsonify({'error': 'Erreur serveur lors du démarrage du bot'}), 500

# 💬 Envoyer un message à un canal Discord
@app.route('/send-message', methods=["GET","POST"])
def send_message():
    data = request.json
    message = data.get('message')
    channel_id = data.get('channel_id')

    if not message or not channel_id:
        return jsonify({'error': 'Message et channel_id requis'}), 400

    try:
        print(f"Envoi du message : {message} au canal {channel_id}")  # Log pour vérifier la requête
        subprocess.run(['python', 'client.py', channel_id, message])
        print("Message envoyé avec succès")  # Log de succès
        return jsonify({'status': 'Message envoyé avec succès !'}), 200
    except Exception as e:
        print(f"Erreur lors de l'envoi du message : {str(e)}")  # Log d'erreur
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
