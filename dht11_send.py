#!/home/admin/venv/bin/python3

import time
import math
import board
import requests
import adafruit_dht
from datetime import datetime


# ============================================================================
# Connexions DHT11 (mòdul de 3 pins) -> Raspberry Pi 3
#
# Opció que has indicat:
# - VCC  -> 5V de la Raspberry Pi (pin físic 2)
# - GND  -> GND (pin físic 6)
# - DATA -> GPIO4 (pin físic 7)
#
# Nota important:
# La Raspberry Pi ja ha d'estar connectada a Internet per Wi‑Fi o cable.
# ============================================================================

DEVICE_TOKEN = "token_de_dispositiu" # S'obté en registrar un disposotiu a aulessocarrad.es
API_URL = "https://aulessocarrad.es/api/v1/readings"
SEND_INTERVAL_S = 300  # 5 minuts (300 segons)

orig_print = print

def print(*args, **kwargs):
    orig_print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}]", *args, **kwargs)

dht = adafruit_dht.DHT11(board.D4)

def read_dht11():
    try:
        temperature = dht.temperature
        humidity = dht.humidity

        if temperature is None or humidity is None:
            return None, None

        if math.isnan(float(temperature)) or math.isnan(float(humidity)):
            return None, None

        return float(temperature), float(humidity)

    except RuntimeError as error:
        print(f"Error de lectura del DHT11: {error}")
        return None, None

def send_reading(temperature, humidity):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEVICE_TOKEN}",
    }

    payload = {
        "temperature": temperature,
        "humidity": humidity,
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=15)

        if response.status_code in (201, 202):
            print(f"Lectura enviada correctament (HTTP {response.status_code})", flush=True)
            return True
        elif response.status_code == 401:
            print("ERROR 401: token invàlid o inactiu", flush=True)
        elif response.status_code == 422:
            print("ERROR 422: dades no vàlides", flush=True)
        elif response.status_code == 429:
            print("❌ ERROR 429: massa peticions; augmenta l'interval")
        else:
            print(f"❌ Error HTTP inesperat: {response.status_code}")
            print(response.text)

    except requests.RequestException as error:
        print(f"Error de xarxa: {error}", flus=True)

    return False

def main():
    print("Monitor DHT11 per a Raspberry Pi", flush=True)
    print("===================================")

    while True:
        temperature, humidity = read_dht11()

        if temperature is not None and humidity is not None:
            print(f"Temperatura: {temperature:.1f} °C | Humitat: {humidity:.1f} %", flush=True)
            send_reading(temperature, humidity)
        else:
            print("No s'ha pogut llegir el sensor", flush=True)

        print("---", flush=True)
        time.sleep(SEND_INTERVAL_S)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAturat per l'usuari", flush=True)
    finally:
        dht.exit()
