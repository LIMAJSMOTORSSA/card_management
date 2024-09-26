# adduserutil.py

from smartcard.System import readers
from smartcard.Exceptions import NoCardException, CardConnectionException
from smartcard.util import toHexString
import datetime
from django.conf import settings
from .models import CardInfo, PassengerCard
import uuid
import secrets
import string


def is_reader_connected():
    try:
        r = readers()
        return len(r) > 0
    except Exception:
        return False

def is_card_present(reader):
    try:
        connection = reader.createConnection()
        connection.connect()
        return True
    except NoCardException:
        return False
    except CardConnectionException:
        return False

def get_reader():
    r = readers()
    if len(r) == 0:
        raise Exception("Aucun lecteur NFC détecté.")
    return r[0]

def wait_for_card(timeout=30):
    """Attend qu'une carte soit présente sur le lecteur."""
    reader = get_reader()
    start_time = datetime.datetime.now()
    while (datetime.datetime.now() - start_time).seconds < timeout:
        if is_card_present(reader):
            return reader
    raise Exception("Aucune carte détectée dans le délai imparti.")

def authenticate_sector(connection, sector, key=None):
    if key is None:
        key = [0xFF] * 6  # Clé par défaut
    sector_trailer_block = sector * 4 + 3
    load_key_command = [0xFF, 0x82, 0x00, 0x00, 0x06] + key
    response, sw1, sw2 = connection.transmit(load_key_command)
    if sw1 != 0x90:
        return False
    authenticate_command = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, sector_trailer_block, 0x60, 0x00]
    response, sw1, sw2 = connection.transmit(authenticate_command)
    return sw1 == 0x90

def read_block(connection, block):
    read_command = [0xFF, 0xB0, 0x00, block, 0x10]
    response, sw1, sw2 = connection.transmit(read_command)
    return response if sw1 == 0x90 else None

def write_block(connection, block, data):
    write_command = [0xFF, 0xD6, 0x00, block, 0x10] + data
    response, sw1, sw2 = connection.transmit(write_command)
    return sw1 == 0x90

def write_to_nfc_card(card_info):
    try:
        if not is_reader_connected():
            raise Exception("Aucun lecteur NFC n'est connecté.")

        reader = wait_for_card()
        connection = reader.createConnection()
        connection.connect()

        sector = 9
        if authenticate_sector(connection, sector):
            blocks = [36, 37, 38]
            
            if not write_block(connection, blocks[0], list(card_info.card_uid.encode().ljust(16, b'\x00'))):
                raise Exception("Échec de l'écriture de l'UID")
            
            secret_code = card_info.get_secret_code()
            if not write_block(connection, blocks[1], list(secret_code.encode().ljust(16, b'\x00'))):
                raise Exception("Échec de l'écriture du code secret")
            
            exp_date = card_info.expiration_date.strftime("%Y-%m-%d").encode()
            if not write_block(connection, blocks[2], list(exp_date.ljust(16, b'\x00'))):
                raise Exception("Échec de l'écriture de la date d'expiration")

            print("Écriture sur la carte NFC réussie")
            return True
        else:
            raise Exception("Échec de l'authentification pour le secteur 9")

    except Exception as e:
        print(f"Erreur lors de l'écriture sur la carte NFC : {str(e)}")
        return False

def read_from_nfc_card():
    try:
        if not is_reader_connected():
            raise Exception("Aucun lecteur NFC n'est connecté.")

        reader = wait_for_card()
        connection = reader.createConnection()
        connection.connect()

        sector = 9
        if authenticate_sector(connection, sector):
            uid = read_block(connection, 36)
            secret_code = read_block(connection, 37)
            exp_date = read_block(connection, 38)
            
            if uid and secret_code and exp_date:
                return {
                    'card_uid': bytes(uid).decode().strip('\x00'),
                    'secret_code': bytes(secret_code).decode().strip('\x00'),
                    'expiration_date': bytes(exp_date).decode().strip('\x00')
                }
            else:
                raise Exception("Échec de la lecture de certaines données")
        else:
            raise Exception("Échec de l'authentification pour le secteur 9")

    except Exception as e:
        print(f"Erreur lors de la lecture de la carte NFC : {str(e)}")
        return None

def verify_nfc_card_for_transaction(passenger_user):
    card_data = read_from_nfc_card()
    if not card_data:
        return False, "Impossible de lire la carte NFC"

    try:
        passenger_card = PassengerCard.objects.get(passenger_user=passenger_user)
        card_info = passenger_card.card_info

        if card_data['card_uid'] != card_info.card_uid:
            return False, "UID de carte non valide"

        if card_data['secret_code'] != card_info.get_secret_code():
            return False, "Code secret non valide"

        exp_date = datetime.datetime.strptime(card_data['expiration_date'], "%Y-%m-%d").date()
        if exp_date < datetime.date.today():
            return False, "Carte expirée"

        return True, "Carte valide"

    except PassengerCard.DoesNotExist:
        return False, "Carte non associée à un utilisateur"
    except Exception as e:
        return False, f"Erreur lors de la vérification : {str(e)}"
    
    
def generate_uid():
    """Génère un identifiant unique pour la carte."""
    return str(uuid.uuid4())[:8]  # Prend les 8 premiers caractères de l'UUID

def generate_secret_code(length=6):
    """Génère un code secret aléatoire."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))
