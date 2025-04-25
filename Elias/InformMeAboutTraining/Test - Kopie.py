import requests
import datetime
import os
from ultralytics import YOLO

def send_discord_webhook(
    webhook_url: str, 
    message: str, 
    csv_path: str = "results.csv",  # Hier ist es 'csv_path' (Singular)
    attach_csv: bool = True
):
    """
    Sendet Training-Update an Discord mit optionalem CSV-Anhang
    
    :param webhook_url: Discord Webhook URL
    :param message: Benutzerdefinierte Nachricht
    :param csv_path: Pfad zur CSV-Datei
    :param attach_csv: Ob CSV als Anhang gesendet werden soll
    """
    try:
        # 1. Zeitstempel erstellen
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"{message}\n\n**Training abgeschlossen um:** {timestamp}"

        # 2. Als reine Textnachricht oder mit Anhang senden
        if not attach_csv or not os.path.exists(csv_path):
            # Fallback: Nur Textnachricht
            payload = {"content": full_message}
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                webhook_url,
                json=payload,
                headers=headers
            )
        else:
            # Mit Dateianhang senden
            with open(csv_path, 'rb') as csv_file:
                files = {
                    'file': (os.path.basename(csv_path), csv_file.read())
                }
                payload = {
                    "content": full_message,
                    "username": "YOLO Training Bot"
                }
                response = requests.post(
                    webhook_url,
                    files=files,
                    data=payload
                )

        # 3. Response prüfen
        if response.status_code not in [200, 204]:
            print(f"⚠️ Fehler beim Senden (Code {response.status_code}): {response.text}")

    except Exception as e:
        print(f"❌ Kritischer Fehler: {str(e)}")
"""
def on_train_end(trainer):
    # Hier müssen wir einen einzelnen Pfad übergeben, nicht eine Liste
    csv_path = f"{trainer.save_dir}/results.csv"
    """
    send_discord_webhook(
        webhook_url="https://discord.com/api/webhooks/1357650449452371998/aJLq2vJMGMFeJ1b-i908XqgTN4MXDS6FeWfr8D1MWRqZhlk9iYBwuznzYBFYNaiSJION",
        #message=f"✅ Training '{trainer.args.name}' abgeschlossen!",
        message=f"Training abgeschlossen"
        csv_path='results.csv'
    )

model = YOLO("yolo11n.pt")
results = model.train(
    data=r"C:\Users\godgo\Downloads\config.yaml",
    epochs=50,
    project='runs/train',
    name='wowee',
    cos_lr=True,
    lr0=0.001,