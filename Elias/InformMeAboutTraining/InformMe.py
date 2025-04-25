import requests

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1357650449452371998/aJLq2vJMGMFeJ1b-i908XqgTN4MXDS6FeWfr8D1MWRqZhlk9iYBwuznzYBFYNaiSJION"

def send_csv_to_discord(csv_file_path):
    try:
        with open(csv_file_path, 'rb') as f:
            files = {'file': (csv_file_path, f, 'text/csv')}
            
            # Zusätzliche Nachricht als Payload
            payload = {
                "content": "Neue CSV-Datei wurde hochgeladen:",
                "username": "Trainings Toni"
            }
            
            response = requests.post(DISCORD_WEBHOOK_URL, files=files, data=payload)
            
            # Erfolgskriterium anpassen
            if response.status_code == 200:
                print("CSV erfolgreich gesendet! Discord Response:", response.json())
                return True
            else:
                print(f"Fehler beim Senden. Statuscode: {response.status_code}, Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"Kritischer Fehler: {str(e)}")
        return False

# Testaufruf
csv_file_path = 'results.csv'
if send_csv_to_discord(csv_file_path):
    print("Alles funktioniert!")
else:
    print("Es gab Probleme beim Upload.")