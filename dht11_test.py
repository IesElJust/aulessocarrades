import time
import board
import adafruit_dht

dht = adafruit_dht.DHT11(board.D4)

while True:
    try:
        temperatura = dht.temperature
        humetat = dht.humidity

        if temperatura and humetat:
            print(f"Temperatura: {temperatura:.1f} ºC | Humetat: {humetat:.1f} %")
        else:
            print("Error llegint les dades")

    except RuntimeError as error:
        print(f"Error de lectura {error}")
    except Exception as error:
        dht.exit()
        raise error

    time.sleep(5)
