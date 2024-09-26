# app_name/nfc_reader.py
from smartcard.System import readers
from smartcard.util import toHexString

def read_nfc_card():
    # Liste des lecteurs NFC connectés
    r = readers()
    if len(r) == 0:
        raise Exception("Aucun lecteur NFC trouvé.")

    # Utiliser le premier lecteur trouvé
    reader = r[0]
    connection = reader.createConnection()
    connection.connect()

    # Envoi d'une commande APDU pour lire la carte
    SELECT = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    data, sw1, sw2 = connection.transmit(SELECT)

    if sw1 == 0x90 and sw2 == 0x00:
        # Retourner les données de la carte sous forme hexadécimale
        return toHexString(data)
    else:
        raise Exception("Impossible de lire la carte NFC.")
