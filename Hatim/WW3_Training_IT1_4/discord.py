import requests
import datetime
import os

def send_discord_webhook(
    webhook_url: str,
    message: str,
    csv_path: str = "results.csv",
    attach_csv: bool = True
):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"{message}\n\n**Training abgeschlossen um:** {timestamp}"

        # Warnung hinzufügen, falls CSV fehlt
        if attach_csv and not os.path.exists(csv_path):
            full_message += "\n\n❌ **HINWEIS: Trainings-CSV nicht gefunden!**"

        if not attach_csv:
            # Nur Textnachricht
            payload = {"content": full_message}
            headers = {"Content-Type": "application/json"}
            response = requests.post(webhook_url, json=payload, headers=headers)
        elif os.path.exists(csv_path):
            # Mit Anhang senden
            with open(csv_path, 'rb') as csv_file:
                files = {'file': (os.path.basename(csv_path), csv_file.read())}
                payload = {"content": full_message, "username": "YOLO Training Bot"}
                response = requests.post(webhook_url, files=files, data=payload)
        else:
            # attach_csv=True, aber CSV existiert nicht → trotzdem Textnachricht
            payload = {"content": full_message}
            response = requests.post(webhook_url, json=payload)

        if response.status_code not in [200, 204]:
            print(f"⚠️ Fehler beim Senden (Code {response.status_code}): {response.text}")

    except Exception as e:
        print(f"❌ Kritischer Fehler: {str(e)}")
