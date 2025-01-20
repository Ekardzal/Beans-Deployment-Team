from flask import Flask, render_template, request, redirect, url_for, session
import requests
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
# Datenbank import
import sqlitecloud
# Dropbox import
import dropbox
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

# Deine Dropbox App-Daten
APP_KEY = "zek0ppvy1tei9cw"
APP_SECRET = "oqp3gw6myhzxt81"
REDIRECT_URI = "http://localhost:5000/callback"  # Stelle sicher, dass dies deine Redirect-URI ist.

@app.route('/check_token')
def check_token():
    access_token = session.get('access_token')

    if access_token:
        try:
            dropbox_client = dropbox.Dropbox(oauth2_access_token=access_token)
            dropbox_client.users_get_current_account()  # API Call, um zu prüfen, ob das Token gültig ist
            return {'status': 'valid'}  # Gültiges Token
        except dropbox.exceptions.AuthError:
            return {'status': 'invalid'}  # Ungültiges Token
    else:
        return {'status': 'missing'}  # Kein Token vorhanden

# Route für Dropbox-Client, die den Authentifizierungsprozess prüft
@app.route('/dropbox_client')
# Schritt 2: Funktion, um den Dropbox-Client mit dem Refresh-Token zu initialisieren
def get_dropbox_client():

    refresh_token = session.get('refresh_token')

    logging.debug(f"refresh_token: {refresh_token}")

    if refresh_token:
        try:
            # Access Token durch Refresh Token erneuern
            response = requests.post("https://api.dropbox.com/oauth2/token", data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": APP_KEY,
                "client_secret": APP_SECRET
            })

            response.raise_for_status()  # Überprüft auf Fehler

            # Access Token extrahieren
            access_token = response.json().get("access_token")

            if access_token:
                # Initialisiere Dropbox-Client mit neuem Access Token
                dropbox_client = dropbox.Dropbox(oauth2_access_token=access_token)
                return dropbox_client
            else:
                print("Kein Access Token erhalten.")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Fehler beim Erneuern des Tokens: {e}")
            return None

    # Wenn kein Refresh Token vorhanden ist, versuche das Access Token
    access_token = session.get('access_token')

    if access_token:
        try:
            dropbox_client = dropbox.Dropbox(oauth2_access_token=access_token)
            # Beispiel-API-Call, um zu überprüfen, ob das Access Token gültig ist
            dropbox_client.users_get_current_account()  # Überprüft, ob das Token noch gültig ist
            return dropbox_client
        except dropbox.exceptions.AuthError as e:
            # Fehler beim Zugriff auf Dropbox, möglicherweise abgelaufenes Access Token
            print(f"Authentifizierungsfehler: {e}")
            return redirect('/authenticate')  # Benutzer zur Authentifizierung umleiten
    else:
        # Falls weder Access Token noch Refresh Token vorhanden sind
        print("Kein Access Token und kein Refresh Token gefunden.")
        return redirect('/authenticate')  # Benutzer zur Authentifizierung umleiten

# Authentifizierungs-Route
@app.route('/authenticate')
def authenticate():
    auth_url = f"https://www.dropbox.com/oauth2/authorize?client_id={APP_KEY}&response_type=code&redirect_uri={REDIRECT_URI}"
    return redirect(auth_url)

# Callback-Route für Dropbox OAuth2
@app.route('/callback')
def callback():
    auth_code = request.args.get('code')
    logging.debug(f"Auth-Code erhalten: {auth_code}")

    # Auth-Code gegen Access-Token tauschen
    response = requests.post(
        "https://api.dropbox.com/oauth2/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": APP_KEY,
            "client_secret": APP_SECRET,
            "redirect_uri": REDIRECT_URI
        }
    )

    if response.status_code == 200:
        tokens = response.json()
        logging.debug(f"Erhaltene Tokens: {tokens}")
        # Access-Token und Refresh-Token extrahieren
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")

        # Speichern des Access Tokens in der Session
        if access_token:
            session['access_token'] = access_token
            logging.debug("Access Token erfolgreich in der Session gespeichert.")
        else:
            logging.error("Fehler: Kein Access Token erhalten.")
            return f"Fehler: Kein Access Token erhalten."

        # Optional: Wenn ein Refresh Token da ist, auch speichern
        if refresh_token:
            session['refresh_token'] = refresh_token
            logging.debug("Refresh Token erfolgreich in der Session gespeichert.")

        return redirect('/')
    else:
        logging.error(f"Fehler beim Abrufen der Tokens: {response.status_code} - {response.text}")
        return f"Fehler: {response.status_code} - {response.text}"


# Funktion zum Erstellen der Tabelle, falls sie noch nicht existiert
def create_table():
    try:
        conn = sqlitecloud.connect('sqlitecloud://cecmlolvhk.g4.sqlite.cloud:8860/ett-database?apikey=t6Rw9LxLwOBziI5Ahmwxn0QDRA1PYGuU0Q2IvTYVrko')
        cursor = conn.cursor()
        result = cursor.fetchone()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_name TEXT NOT NULL,
                analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                predictions TEXT,
                bounding_boxes TEXT,
                image_url TEXT
            )
        ''')

        conn.commit()
        logging.debug("Tabelle 'analysis_results' erfolgreich erstellt oder existiert bereits.")
    except sqlitecloud.exceptions.SQLiteCloudOperationalError as e:
        logging.error(f"Datenbankfehler bei der Tabellenerstellung: {e}")
    finally:
        conn.close()


create_table()

# Funktion zum Hochladen des Bildes zu Dropbox
def upload_image_with_boxes_to_dropbox(image_with_boxes, image_name, dropbox_client):
    # Dropbox-Client initialisieren
    #dropbox_client = get_dropbox_client()

    if not dropbox_client:
        logging.error("Fehler beim Initialisieren des Dropbox-Clients.")
        return None
    try:
        # Dropbox-Pfad erstellen
        dropbox_path = f"/endpoint-testing-tool/{image_name}"

        # Bild in Bytes umwandeln und zu Dropbox hochladen
        image_data = base64.b64decode(image_with_boxes)
        response = dropbox_client.files_upload(image_data, dropbox_path, mode=dropbox.files.WriteMode.overwrite)

        # Einen öffentlichen Link zum Bild erstellen
        # Überprüfen, ob bereits ein freigegebener Link für die Datei existiert
        try:
            shared_link_metadata = dropbox_client.sharing_create_shared_link_with_settings(response.path_lower)
        except dropbox.exceptions.ApiError as e:
            # Wenn der Fehler 'shared_link_already_exists' auftritt, den bestehenden Link verwenden
            if e.error.is_shared_link_already_exists():
                shared_link_metadata = dropbox_client.sharing_get_shared_link_metadata(response.path_lower)
            else:
                raise e
        logging.debug(f"shared_link_metadata = {shared_link_metadata}")

        # Den direkten Link zum Bild zurückgeben, falls er verfügbar ist (ersetze ?dl=0 mit ?raw=1)
        image_url = shared_link_metadata.url.replace('dl=0', 'dl=1')

        return image_url

        # Debug-Ausgabe, um zu überprüfen, ob der Link korrekt ist
        logging.debug(f"Modified shared link: {image_url}")

    except Exception as e:
        logging.error(f"Fehler beim Hochladen des Bildes nach Dropbox: {e}")
        return None

# Dein Modell oder die Abfrage direkt hier definieren
def get_items_from_db():
    try:
        # Verbindung zur Cloud-Datenbank herstellen
        conn = sqlitecloud.connect('sqlitecloud://cecmlolvhk.g4.sqlite.cloud:8860/ett-database?apikey=t6Rw9LxLwOBziI5Ahmwxn0QDRA1PYGuU0Q2IvTYVrko')
        cursor = conn.cursor()
        # Abfrage ausführen
        cursor.execute("SELECT * FROM analysis_results")
        items = cursor.fetchall()

        # Überprüfe, wie viele Spalten in den Zeilen vorhanden sind
        for row in items:
            print(f"Row: {row}, Spaltenanzahl: {len(row)}")

        formatted_rows = []
        for row in items:
            # Überprüfe hier, wie viele Werte jede Zeile hat
            print(f"Row: {row}, Spaltenanzahl: {len(row)}")  # Debugging Zeile

            if len(row) < 4:  # Wenn weniger als 4 Spalten vorhanden sind, überspringen
                print(f"Zeile übersprungen: {row}")
                continue

            # Entpacken der ersten 4 Spalten (image_name, analysis_time, predictions, bounding_boxes)
            image_name, analysis_time, predictions, bounding_boxes = row[:4]  # Sicherstellen, dass nur 4 Spalten entpackt werden

            # Versuche, die `predictions` und `bounding_boxes` als JSON zu deserialisieren
            try:
                predictions_data = json.loads(predictions)  # JSON deserialisieren
            except json.JSONDecodeError:
                print(f"Fehler beim Decodieren von predictions: {predictions}")
                predictions_data = []  # Fallback, falls Fehler auftritt

            try:
                bounding_boxes_data = json.loads(bounding_boxes)  # JSON deserialisieren
            except json.JSONDecodeError:
                print(f"Fehler beim Decodieren von bounding_boxes: {bounding_boxes}")
                bounding_boxes_data = []  # Fallback, falls Fehler auftritt

            # Extrahiere relevante Daten (z.B. Klassenname und Confidence) aus predictions
            formatted_predictions = extract_relevant_data(predictions_data)

            # Füge das formatierte Item zu formatted_rows hinzu
            formatted_rows.append({
                "image_name": image_name,
                "predictions": formatted_predictions,
                "bounding_boxes": bounding_boxes_data
            })

        #return formatted_rows
        return items

    except Exception as e:
        print("Datenbankfehler:", e)
    finally:
        conn.close()  # Verbindung immer schließen

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

# Funktion, um die predictions zu formatieren
def extract_relevant_data(predictions_data):
    relevant_data = []
    if isinstance(predictions_data, list):
        for prediction in predictions_data:
            # Extrahiere relevante Daten (z.B. Klassennamen und Confidence)
            class_name = prediction.get("class", "Unbekannt")  # Beispiel: nehme "class" als Attribut
            confidence = prediction.get("confidence", 0)  # Beispiel: nehme "confidence" als Attribut
            relevant_data.append({"class_name": class_name, "confidence": confidence})
    return relevant_data

# Route für das Hochladen des Bildes und die Analyse
@app.route('/')
def index():
    # Überprüfen, ob der Benutzer authentifiziert ist
    #access_token = session.get('access_token', None)
    # Überprüfen, ob das refresh_token in der Session vorhanden ist
    #refresh_token = session.get('refresh_token')
    #logging.debug(f"Session Refresh Token: {refresh_token}")

    # Das Analyseergebnis und die Zeiten aus der Session holen (falls vorhanden)
    result = session.get('result', None)
    request_time = session.get('request_time', None)
    end_time = session.get('end_time', None)
    # Rückgabe der Daten an das HTML-Template
    return render_template('test_html_gui.html', result=result, request_time=request_time, end_time=end_time)

@app.route('/database')
def database():
    items = get_items_from_db()  # Holen der Datenbankinhalte

    # Beispiel für Umwandlung der Tupel in Dictionaries
    items = [
        {"image_name": row[1], "analysis_time": row[2], "predictions": json.loads(row[3]), "bounding_boxes": json.loads(row[4]), "image_url": row[5]}
        for row in items
    ]
    return render_template('ett_database.html', items=items)

@app.route('/scripts')
def show_scripts():
    return render_template('test_show_scripts.html')
    
@app.route('/analyse', methods=['POST'])
def analyse():
    # Bild vom Formular erhalten
    image_file = request.files['image']
    #----------------------------------------------------------NEU
    save_file = request.form.get('saveFile') == 'true'  # Überprüfen, ob das Häkchen gesetzt ist
    save_database = request.form.get('saveDatabase') == 'true'  # Überprüfen, ob das Häkchen gesetzt ist
    
    # Base64-kodiertes Bild
    encoded_image = encode_image(image_file)
    
    # Startzeit der Anfrage
    request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Daten für die Anfrage
    data = {
        "image": encoded_image,
        #nicht mehr notwendig-> "ext": image_file.filename.split('.')[-1]
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

         # Extrahiere die erkannten Klassen und Confidence-Werte
        detected_classes = []
        bounding_boxes = []
        for prediction in response_json.get('predictions:', []):
            if isinstance(prediction, list):
                for pred in prediction:
                    class_name = pred.get('name', 'Unbekannt')
                    confidence = pred.get('confidence', 0.0)  # Fallback-Wert, falls nicht vorhanden

                    # Füge Klasse und Confidence hinzu
                    detected_classes.append({"name": class_name, "confidence": confidence})

                    # Debugging: Logge den Klassennamen
                    logging.debug(f"------------------------------------------ Found class: {class_name}")

                    # Füge Bounding-Box hinzu, falls vorhanden
                    box = pred.get('box')
                    if box:
                        bounding_boxes.append({
                            "x1": box["x1"],
                            "y1": box["y1"],
                            "x2": box["x2"],
                            "y2": box["y2"],
                            "name": class_name
                        })
                    logging.debug(f"------------------------------------------ Bounding boxes received: {bounding_boxes}")

        # Berechne die Dauer der Anfragebearbeitung
        duration = int(end_time - start_time)  # Wandelt die Dauer in eine Ganzzahl um
            
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

        # Wenn das Häkchen gesetzt ist, speichere die Ergebnisse in einer Logdatei
        if save_file:
            save_analysis_to_files(image_file.filename, response_json, img)


        if save_database:
            # Versuche, den Dropbox-Client zu erhalten
            dropbox_client = get_dropbox_client()
            # Überprüfe, ob der Dropbox-Client erfolgreich erstellt wurde
            if isinstance(dropbox_client, dropbox.Dropbox):
                # Bild mit Bounding Boxen in Dropbox hochladen und URL erhalten
                image_url = upload_image_with_boxes_to_dropbox(encoded_image_with_boxes, image_file.filename, dropbox_client)
            else:
                # Wenn kein Dropbox-Client vorhanden ist, wird der Benutzer zur Authentifizierung weitergeleitet
                return redirect('/authenticate')  # Benutzer zur Authentifizierung umleiten

            save_analysis_to_db(image_file.filename, response_json, bounding_boxes, image_url)  # Hier wird die Datenbankfunktion aufgerufen

        # Gib das Bild und die Ergebnisse direkt an das Template zurück
        return render_template('test_html_gui.html',
                               result=session['result'],
                               request_time=request_time,
                               end_time=end_time,
                               duration=duration,  # Dauer an das Template übergeben
                               image=encoded_image_with_boxes,
                               detected_classes=detected_classes)  # Übergebe das bearbeitete Bild an das Template

    except urllib.error.HTTPError as e:
        return f"HTTP-Fehler: {e.code} - {e.read().decode('utf-8')}"
    except urllib.error.URLError as e:
        return f"URL-Fehler: {e.reason}"
    except Exception as e:
        return f"Ein Fehler ist aufgetreten: {e}"

@app.route('/test', methods=['GET'])
def test_route():
    # Base64-kodiertes Bild (hier ein Beispielbild, das du weiterverwenden kannst)
    encoded_image = "/9j/4AAQSkZJRgABAQIAJQAlAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////2wBDAf//////////////////////////////////////////////////////////////////////////////////////wgARCABLAEkDAREAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAAAAEC/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAH/2gAMAwEAAhADEAAAAYIpAACUKWFSAqiM0KWAAAM0BqAAAM0BYVACiJQAFikJQAAohVjNAAAAAAAAAAAAAWJVIAD/xAAUEAEAAAAAAAAAAAAAAAAAAABg/9oACAEBAAEFAkn/xAAUEQEAAAAAAAAAAAAAAAAAAABg/9oACAEDAQE/AUn/xAAUEQEAAAAAAAAAAAAAAAAAAABg/9oACAECAQE/AUn/xAAUEAEAAAAAAAAAAAAAAAAAAABg/9oACAEBAAY/Akn/xAAWEAEBAQAAAAAAAAAAAAAAAAARUBD/2gAIAQEAAT8hqmE3/9oADAMBAAIAAwAAABAZbbKQIZQOQf8A7/kn/wC+4JhJBoJJnpAIBgoAIAAAAIAAAJJIoJJP/8QAFBEBAAAAAAAAAAAAAAAAAAAAYP/aAAgBAwEBPxBJ/8QAFBEBAAAAAAAAAAAAAAAAAAAAYP/aAAgBAgEBPxBJ/8QAHBAAAwEAAwEBAAAAAAAAAAAAAAERECAxUTBA/9oACAEBAAE/EKUpSlKVlKLsmTWvCD7xd6smvvVwTxj1MbvBMb5IRD8c04xsT9Kh/qXw/9k="
    
    # Decodiere und speichere das Bild als Datei -> Zum Testen ob Base64 richtig oben angebebn
    #with open("test_image_base64.jpg", "wb") as f:
        #f.write(base64.b64decode(encoded_image))
    
    # Anfrage an den Azure-Endpunkt senden
    try:
        # Startzeit der Anfrage
        start_time = time.time()
        
        # Daten für die Anfrage
        data = {
            "image": encoded_image,
        }
        body = json.dumps(data).encode("utf-8")
        
        # Header für die Anfrage
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Anfrage an den Azure-Endpunkt senden
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            response_content = response.read().decode("utf-8")
            response_json = json.loads(response_content)
            
            # Antwortzeit und Status
            end_time = time.time()
            duration = int(end_time - start_time)  # Dauer der Anfragebearbeitung
            
            # Überprüfen, ob die Antwort erfolgreich war
            if response.status == 200:
                status_message = "Endpoint ist responding: {}s".format(duration)
                svg_class = 'success'  # Setze die Klasse auf 'success' für grün
            else:
                status_message = f"Fehler bei der Anfrage: {response.status}. Dauer: {duration} Sekunden"
                svg_class = 'error'  # Setze die Klasse auf 'error' für rot
            return render_template('test_html_gui.html', status_message=status_message, svg_class=svg_class)
    
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

# Funktion zum Speichern der Analyseergebnisse in der SQLite-Datenbank
def save_analysis_to_db(image_name, analysis_result, bounding_boxes, image_url):
    try:
        conn = sqlitecloud.connect("sqlitecloud://cecmlolvhk.g4.sqlite.cloud:8860/ett-database?apikey=t6Rw9LxLwOBziI5Ahmwxn0QDRA1PYGuU0Q2IvTYVrko")
        cursor = conn.cursor()

        predictions = json.dumps(analysis_result)
        bounding_boxes = json.dumps(bounding_boxes)

        # Einfügen der Daten, einschließlich des Dropbox-Links
        cursor.execute('''
            INSERT INTO analysis_results (image_name, predictions, bounding_boxes, image_url)
            VALUES (?, ?, ?, ?)
        ''', (image_name, predictions, bounding_boxes, image_url))

        conn.commit()
        logging.debug(f"Analyseergebnisse für {image_name} in der Datenbank gespeichert.")

    except sqlitecloud.exceptions.SQLiteCloudOperationalError as e:
        logging.error(f"Datenbankfehler: {e}")
    finally:
        conn.close()

# Funktion zum Öffnen des Ordners
@app.route('/open-folder', methods=['GET'])
def open_folder():
    if os.path.exists(UPLOAD_FOLDER):
        os.startfile(UPLOAD_FOLDER)  # Öffnet den Ordner im Explorer (Windows)
        return "Ordner geöffnet!", 200
    else:
        return "Ordner existiert nicht!", 404

if __name__ == '__main__':
    app.run(debug=True)
