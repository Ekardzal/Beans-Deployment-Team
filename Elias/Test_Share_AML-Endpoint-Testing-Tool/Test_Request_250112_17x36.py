from flask import Flask, render_template, request, redirect, url_for, session
#Daten über "redirect" & "url_for" weitergeben, damit sie auf tartseite verfügbar sind. Eine Möglichkeit = Verwendung von Flask's session-Mechanismus, um Ergebnisse zwischen Routen zu speichern.
import json
import base64
import os
import urllib.request
# "datetime" nötig für Zeitangaben
from datetime import datetime
# Nötig für Angabe der Analysze Zeit
import time
#Nötige Imports für Bounding Box Zeichnung von Pillow
from PIL import Image, ImageDraw, ImageFont
import io
from flask_swagger_ui import get_swaggerui_blueprint
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# URL für Swagger-UI und Pfad zur OpenAPI-Datei
SWAGGER_URL = '/swagger'
API_SPEC_URL = '/static/openapi.yaml'

# Swagger-UI Blueprint einrichten
swagger_ui = get_swaggerui_blueprint(SWAGGER_URL, API_SPEC_URL)
app.register_blueprint(swagger_ui, url_prefix=SWAGGER_URL)

# Geheimen Schlüssel setzen, der für die Sitzung benötigt wird
app.secret_key = 'beans'

# Ordner für gespeicherte Textdateien
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Funktion zum Laden und Kodieren eines Bildes
def encode_image(image_file):
    """
    Liest ein Bild und kodiert es in Base64.
    :param image_file: Bilddatei (vom Benutzer hochgeladen).
    :return: Base64-kodiertes Bild als String.
    """
    logging.debug("------------------------------------------ Encoding image to base64.")
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
    #----------------------------------------------------------NEU
    save_file = request.form.get('saveFile') == 'true'  # Überprüfen, ob das Häkchen gesetzt ist
    
    # Base64-kodiertes Bild
    encoded_image = encode_image(image_file)
    
    # Startzeit der Anfrage
    request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Daten für die Anfrage
    data = {
        "image": encoded_image,
        # nicht mehr notwendig-> "ext": image_file.filename.split('.')[-1]
    }
    body = json.dumps(data).encode("utf-8")

    # Header für die Anfrage
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        # Zeit vor der Anfrage messen
        start_time = time.time()
        
        # Anfrage an den Azure-Endpunkt senden
        logging.debug(f"------------------------------------------ Sending request to Azure endpoint: {url}")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            response_content = response.read().decode("utf-8")
            response_json = json.loads(response_content)
            # Zeit nach der Anfrage messen
            end_time = time.time()
            logging.debug(f"------------------------------------------ Received response: {response_json}")

            # Berechne die Dauer der Anfragebearbeitung
            duration = int(end_time - start_time)  # Wandelt die Dauer in eine Ganzzahl um
    
            # Debugging: Überprüfe alle Klassennamen in der JSON-Antwort
            for prediction in response_json.get('predictions:', []):
                if isinstance(prediction, list):
                    for pred in prediction:
                        class_name = pred.get('name', 'Unbekannt')
                        logging.debug(f"------------------------------------------ Found class: {class_name}")
        
            # Extrahiere Bounding Boxen aus der Antwort
            bounding_boxes = []
            for prediction in response_json.get('predictions:', []):
                if isinstance(prediction, list):
                    for pred in prediction:
                        box = pred.get('box')
                        class_name = pred.get('name', 'Unbekannt')  # Standardwert 'Unbekannt', falls 'name' fehlt
                        if box:
                            bounding_boxes.append({
                                "x1": box["x1"],
                                "y1": box["y1"],
                                "x2": box["x2"],
                                "y2": box["y2"],
                                "name": class_name
                            })
            logging.debug(f"------------------------------------------ Bounding boxes received: {bounding_boxes}")
            
            # Lade das Bild mit Pillow
            img = Image.open(io.BytesIO(base64.b64decode(encoded_image)))
            
            # Modus überprüfen und ggf. konvertieren
            if img.mode == "RGBA":
                img = img.convert("RGB")  # Alpha-Kanal entfernen
    
            draw = ImageDraw.Draw(img)

            # Zeichne die Bounding Boxen und Klassennamen auf das Bild
            for pred in bounding_boxes:
                if pred:
                    x1, y1, x2, y2 = pred['x1'], pred['y1'], pred['x2'], pred['y2']
                    class_name = pred['name']  # Klassennamen aus der Bounding Box
                    logging.debug(f"------------------------------------------ Drawing bounding box: ({x1}, {y1}, {x2}, {y2})")
                    draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                    
                    # Schriftart und -größe festlegen
                    try:
                        font_path = "/fonts/arial.ttf"  # Pfad zur Schriftartdatei
                        font_size = 60  # Schriftgröße anpassen
                        font = ImageFont.truetype(font_path, font_size)
                    except:
                        font = None  # Falls die Schriftart nicht gefunden wird, Standard verwenden
                        
                    draw.text((x1, y1 - 10), class_name, fill="red", font=font)  # Text oberhalb der Bounding Box
            
            # Speichere das bearbeitete Bild als Base64
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)
            encoded_image_with_boxes = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
            logging.debug(f"------------------------------------------ Encoded image with bounding boxes size: {len(encoded_image_with_boxes)} bytes")
            
            # Endzeit der Analyse
            end_time = datetime.now().strftime("%d-%m-%y %H:%M:%S")
            
            # Speichere Ergebnisse in der Session
            session['result'] = json.dumps(response_json, indent=4)
            session['request_time'] = request_time
            session['end_time'] = end_time
            session['duration'] = duration  # Dauer in der Session speichern
            
            #----------------------------------------------------------NEU
            # Wenn das Häkchen gesetzt ist, speichere die Ergebnisse in einer Logdatei
            if save_file:
                save_analysis_to_files(image_file.filename, response_json, img)
                
            # Gib das Bild und die Ergebnisse direkt an das Template zurück
            return render_template('test_html_gui.html', 
                                   result=session['result'], 
                                   request_time=request_time, 
                                   end_time=end_time,
                                   duration=duration,  # Dauer an das Template übergeben
                                   image=encoded_image_with_boxes)  # Übergebe das bearbeitete Bild an das Template
            
    except urllib.error.HTTPError as e:
        return f"HTTP-Fehler: {e.code} - {e.read().decode('utf-8')}"
    except urllib.error.URLError as e:
        return f"URL-Fehler: {e.reason}"
    except Exception as e:
        return f"Ein Fehler ist aufgetreten: {e}"
        
# Funktion, um Analyseergebnisse und bearbeitete Bilder zu speichern
def save_analysis_to_files(image_name, analysis_result, img):
    # Zeitstempel für die Dateinamen
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Dateinamen für Textdatei und Bild
    base_name = f"{timestamp}_{image_name.replace('.', '_')}"
    output_textfile = os.path.join(UPLOAD_FOLDER, f"{base_name}_predictions.txt")
    output_imagefile = os.path.join(UPLOAD_FOLDER, f"{base_name}.jpg")
    
    # Speichern der Ergebnisse in der Textdatei
    with open(output_textfile, 'w') as file:
        file.write(f"Bildname: {image_name}\n")
        file.write(f"Analyse durchgeführt am: {timestamp}\n")
        file.write("\n")
        file.write("Ergebnisse der Analyse:\n")
        json.dump(analysis_result, file, indent=4)
    logging.debug(f"Analyseergebnisse gespeichert in: {output_textfile}")
    
    # Skalieren des Bildes
    new_width = img.width // 2  # Reduziere Größe um 50 %
    new_height = img.height // 2
    scaled_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)  # Hochwertiges Resampling

    
    # Speichern des bearbeiteten Bildes
    scaled_img.save(output_imagefile, format="JPEG", quality=80)
    logging.debug(f"Bearbeitetes Bild gespeichert in: {output_imagefile}")

if __name__ == '__main__':
    app.run(debug=True)
