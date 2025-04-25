from locust import HttpUser, task, between, events
import base64
import os
import json
import time
import matplotlib.pyplot as plt

# Konfiguration
API_KEY = "EOLqlbiHInFPB2qj5s7L0mqZHWvxOnoASrgub3odRS3tpaTuhoN0JQQJ99BCAAAAAAAAAAAAINFRAZML3lyt"  # AML-Endpunkt-Key
TEST_IMAGES = [
    "images/small.png",   # Kleines Bild (10KB)
    "images/medium.png",  # Mittel (100KB)
    "images/large.png"    # Groß (1MB+)
]
FAILURE_LIMIT = 0.05  # Max. akzeptable Fehlerrate (5%)

class AMLUser(HttpUser):
    host = "https://endpunkt-mjyxx.germanywestcentral.inference.ml.azure.com"  # Hier die Basis-URL eintragen
    wait_time = between(0.1, 0.5)

    def on_start(self):
        self.headers = {"Authorization": f"Bearer {API_KEY}"}
        self.image_pool = [self.encode_image(path) for path in TEST_IMAGES]

    def encode_image(self, path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    @task(3)
    def test_small_image(self):
        self.send_request(self.image_pool[0])

    @task(2)
    def test_medium_image(self):
        self.send_request(self.image_pool[1])

    @task(1)
    def test_large_image(self):
        self.send_request(self.image_pool[2])

    def send_request(self, image_data):
        payload = {"image": image_data}
        start_time = time.time()
        
        with self.client.post(
            "/score",  # AML-Endpoint-Pfad
            json=payload,
            headers=self.headers,
            catch_response=True
        ) as response:
            latency = (time.time() - start_time) * 1000  # in ms
            
            # Tracke benutzerdefinierte Metriken
            response.event_type = "yolo_ocr"
            response.metadata = {
                "image_size": len(image_data),
                "latency": latency
            }
            
            if response.status_code != 200:
                response.failure(f"Code: {response.status_code}")
            elif latency > 10000:  # 10s Timeout-Schwelle
                response.failure(f"Timeout: {latency}ms")

# Daten für Grafiken sammeln
all_requests = []

@events.request.add_listener
def track_request(request_type, name, response_time, response_length, exception, **kwargs):
    if request_type == "yolo_ocr":
        all_requests.append({
            "timestamp": time.time(),
            "latency": response_time,
            "image_size": kwargs.get("image_size", 0),
            "success": exception is None
        })

# Grafiken nach Test generieren
@events.test_stop.add_listener
def generate_report(**kwargs):
    # Durchsatz vs. Fehler
    plt.figure(figsize=(12, 6))
    
    # Latenzverteilung
    plt.subplot(1, 2, 1)
    latencies = [r["latency"] for r in all_requests if r["success"]]
    plt.hist(latencies, bins=50, alpha=0.7, color='blue')
    plt.title('Antwortzeiten-Verteilung (Erfolgreich)')
    plt.xlabel('ms')
    plt.ylabel('Anzahl')
    
    # Fehler nach Bildgröße
    plt.subplot(1, 2, 2)
    failed = [r for r in all_requests if not r["success"]]
    sizes = [r["image_size"] for r in failed]
    plt.scatter(sizes, [r["latency"] for r in failed], c='red', alpha=0.5)
    plt.title('Fehler nach Bildgröße/Timeout')
    plt.xlabel('Bildgröße (Bytes)')
    plt.ylabel('Latenz (ms)')
    
    plt.tight_layout()
    plt.savefig('aml_loadtest_report.png')
    print("Report generated: aml_loadtest_report.png")