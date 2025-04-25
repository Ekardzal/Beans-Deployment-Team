import requests

# Deine Webhook-URL
WEBHOOK_URL = 'https://discord.com/api/webhooks/1357650449452371998/aJLq2vJMGMFeJ1b-i908XqgTN4MXDS6FeWfr8D1MWRqZhlk9iYBwuznzYBFYNaiSJION'

def send_message(message):
    data = {
        "content": message
    }
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code != 200:
        print(f"Fehler beim Senden der Nachricht: {response.status_code}")

# Beispiel, wie du nach jeder Epoche eine Nachricht senden kannst:
def on_epoch_end(epoch, logs):
    # Beispielwerte, die du anpassen kannst:
    loss = logs['loss']
    accuracy = logs['accuracy']

    # Nachricht zusammenstellen
    message = f"Epoche {epoch+1} abgeschlossen! Verlust: {loss:.4f}, Genauigkeit: {accuracy*100:.2f}%"
    
    # Nachricht senden
    send_message(message)

# Dies könnte Teil deiner Trainingsschleife sein:
# on_epoch_end(epoch, logs)
