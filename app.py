from flask import Flask, render_template, request, redirect, url_for, flash
from telethon import TelegramClient
import asyncio
import threading

# Remplis ces valeurs avec tes informations
api_id = '5794256'
api_hash = '5d13de585605b797cad6468a33a01ac2'

# Crée un client pour chaque compte Telegram
clients = []

# Liste des comptes (Numéro de téléphone ou session)
accounts = ["+33745734115", "+33759014400"]

# Créer une instance Flask
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Pour les flash messages

# Fonction pour démarrer la connexion à Telegram dans un thread séparé
def start_telegram_clients():
    asyncio.run(main())

async def main():
    global clients
    for account in accounts:
        client = TelegramClient(account, api_id, api_hash)
        await client.start()  # Démarre la session
        clients.append(client)
        print(f"Connecté à Telegram pour {account}")

    # Garder les sessions actives
    await asyncio.gather(*[client.run_until_disconnected() for client in clients])

# Route pour la page principale
@app.route('/')
def index():
    return render_template('index.html')  # Crée un fichier index.html pour l'interface

# Route pour envoyer un message depuis tous les comptes
@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    
    # Envoie le message depuis chaque compte
    async def send_messages():
        for client in clients:
            await client.send_message('me', message)
        return "Message envoyé avec succès à tous les comptes!"

    try:
        # Exécute l'envoi du message dans un thread séparé
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(send_messages())
        flash(result, 'success')
    except Exception as e:
        flash(f"Erreur: {str(e)}", 'error')

    return redirect(url_for('index'))

# Démarrer l'application web dans un thread
if __name__ == "__main__":
    threading.Thread(target=start_telegram_clients).start()
    app.run(debug=False, host="0.0.0.0", use_reloader=False)
