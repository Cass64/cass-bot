from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'message': 'API Discord-Bot en ligne ! 🚀'})

@app.route('/start-bot', methods=["GET", "POST"])
def start_bot():
    try:
        print("Démarrage du bot...")
        # Démarrer le bot en arrière-plan
        process = subprocess.Popen(['python', 'start.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()  # Capturer la sortie et les erreurs
        print("Sortie du bot :", stdout.decode())
        print("Erreurs du bot :", stderr.decode())
        print("Bot démarré avec succès")
        return jsonify({'status': 'Bot démarré avec succès !'}), 200
    except Exception as e:
        print(f"Erreur lors du démarrage du bot : {str(e)}")
        return jsonify({'error': 'Erreur serveur lors du démarrage du bot', 'details': str(e)}), 500

@app.route('/send-message', methods=["GET", "POST"])
def send_message():
    data = request.json
    message = data.get('message')
    channel_id = data.get('channel_id')

    if not message or not channel_id:
        return jsonify({'error': 'Message et channel_id requis'}), 400

    try:
        print(f"Envoi du message : {message} au canal {channel_id}")
        # Exécuter le script client.py pour envoyer le message
        process = subprocess.run(['python', 'client.py', channel_id, message], capture_output=True, text=True)
        print("Sortie du script :", process.stdout)
        print("Erreurs du script :", process.stderr)
        print("Message envoyé avec succès")
        return jsonify({'status': 'Message envoyé avec succès !'}), 200
    except Exception as e:
        print(f"Erreur lors de l'envoi du message : {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
