from flask import Flask, render_template, request, redirect, url_for, session
#Daten über "redirect" & "url_for" weitergeben, damit sie auf tartseite verfügbar sind. Eine Möglichkeit, ist es, Verwendung von Flask's session-Mechanismus, um Ergebnisse zwischen Routen zu speichern.
import json
import base64
import os
import urllib.request
# "datetime" nötig für Zeitangaben
from datetime import datetime

app = Flask(__name__)

# Geheimen Schlüssel setzen, der für die Sitzung benötigt wird
app.secret_key = 'beans'

# Funktion zum Laden und Kodieren eines Bildes
def encode_image(image_file):
    """
    Liest ein Bild und kodiert es in Base64.
    :param image_file: Bilddatei (vom Benutzer hochgeladen).
    :return: Base64-kodiertes Bild als String.
    """
    return base64.b64encode(image_file.read()).decode("utf-8")

# Endpoint-URL (ersetze mit deinem tatsächlichen Endpoint)
url = "https://end.westeurope.inference.ml.azure.com/score"

# API-Schlüssel (ersetze mit deinem tatsächlichen Schlüssel)
api_key = 'NLBHsesgjYRkev4IWqj0fASuXu3PlsVi'

# Route für das Hochladen des Bildes und die Analyse
@app.route('/')
def index():
    # Das Analyseergebnis und die Zeiten aus der Session holen (falls vorhanden)
    result = session.get('result', None)
    request_time = session.get('request_time', None)
    end_time = session.get('end_time', None)
    return render_template('test_html_gui.html', result=result, request_time=request_time, end_time=end_time)

@app.route('/scripts')
def show_scripts():
    return render_template('test_show_scripts.html')
    
@app.route('/analyse', methods=['POST'])
def analyse():
    # Bild vom Formular erhalten
    image_file = request.files['image']
    
    # Base64-kodiertes Bild
    encoded_image = encode_image(image_file)
    
    # Startzeit der Anfrage
    request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Daten für die Anfrage
    data = {
        "image": encoded_image,
        "ext": image_file.filename.split('.')[-1]
    }
    body = json.dumps(data).encode("utf-8")

    # Header für die Anfrage
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        # Anfrage an den Azure-Endpunkt senden
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            response_content = response.read().decode("utf-8")
            response_json = json.loads(response_content)
            
            # Endzeit der Analyse
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Speichere Ergebnisse in der Session
            session['result'] = json.dumps(response_json, indent=4)
            session['request_time'] = request_time
            session['end_time'] = end_time
            
            # Gib das Bild und die Ergebnisse direkt an das Template zurück
            return render_template('test_html_gui.html', 
                                   result=session['result'], 
                                   request_time=request_time, 
                                   end_time=end_time, 
                                   image=encoded_image)  # Übergebe das Base64-Bild an das Template
            
    except urllib.error.HTTPError as e:
        return f"HTTP-Fehler: {e.code} - {e.read().decode('utf-8')}"
    except urllib.error.URLError as e:
        return f"URL-Fehler: {e.reason}"
    except Exception as e:
        return f"Ein Fehler ist aufgetreten: {e}"

if __name__ == '__main__':
    app.run(debug=True)
