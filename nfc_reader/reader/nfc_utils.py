from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import CardConnectionException, NoCardException

def get_uid(connection):
    get_uid_command = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    try:
        response, sw1, sw2 = connection.transmit(get_uid_command)
        if sw1 == 0x90 and sw2 == 0x00:
            uid = toHexString(response)
            return uid.replace(' ', '').upper()
        else:
            print(f"Erreur lors de la récupération de l'UID : {sw1:02X} {sw2:02X}")
            return None
    except NoCardException:
        print("Erreur : Aucune carte n'est présente sur le lecteur.")
        return None
    except CardConnectionException as e:
        print(f"Exception lors de la récupération de l'UID : {e}")
        return None

def get_atr(connection):
    try:
        atr = connection.getATR()
        atr_hex = toHexString(atr)
        return atr_hex
    except NoCardException:
        print("Erreur : Aucune carte n'est présente sur le lecteur.")
        return None
    except CardConnectionException as e:
        print(f"Exception lors de la récupération de l'ATR : {e}")
        return None

def authenticate_sector(connection, sector_number, key):
    sector_trailer_block = sector_number * 4 + 3

    load_key_command = [0xFF, 0x82, 0x00, 0x00, 0x06] + key
    try:
        response, sw1, sw2 = connection.transmit(load_key_command)
        if sw1 != 0x90:
            print(f"Erreur lors du chargement de la clé : {sw1:02X} {sw2:02X}")
            return False

        authenticate_command = [
            0xFF, 0x86, 0x00, 0x00, 0x05,
            0x01, 0x00, sector_trailer_block, 0x60, 0x00
        ]
        response, sw1, sw2 = connection.transmit(authenticate_command)
        if sw1 != 0x90:
            print(f"Échec de l'authentification pour le secteur {sector_number} : {sw1:02X} {sw2:02X}")
            return False

        return True
    except NoCardException:
        print("Erreur : Aucune carte n'est présente sur le lecteur.")
        return False
    except CardConnectionException as e:
        print(f"Exception lors de l'authentification : {e}")
        return False

def read_block(connection, block_number):
    read_command = [0xFF, 0xB0, 0x00, block_number, 0x10]
    try:
        response, sw1, sw2 = connection.transmit(read_command)
        if sw1 == 0x90 and sw2 == 0x00:
            return response
        else:
            return None
    except NoCardException:
        print("Erreur : Aucune carte n'est présente sur le lecteur.")
        return None
    except CardConnectionException as e:
        print(f"Exception lors de la lecture du bloc {block_number} : {e}")
        return None

def is_block_empty(block_data):
    return all(byte == 0x00 for byte in block_data)

def read_sector_data(connection, sector_number, key):
    if not authenticate_sector(connection, sector_number, key):
        print(f"Impossible d'authentifier le secteur {sector_number}.")
        return None

    data_found = False
    sector_data = {}

    for block_offset in range(3):
        global_block = sector_number * 4 + block_offset
        block_data = read_block(connection, global_block)
        
        if block_data and not is_block_empty(block_data):
            ascii_data = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in block_data])
            hex_data = toHexString(block_data)
            sector_data[global_block] = {"ascii": ascii_data, "hex": hex_data}
            data_found = True

    return sector_data if data_found else None

def write_block(connection, block_number, data):
    if len(data) > 16:
        print(f"Les données dépassent la limite d'un bloc (16 octets).")
        return False

    data_bytes = list(data.encode('utf-8')) if isinstance(data, str) else list(data)
    data_bytes += [0x00] * (16 - len(data_bytes))  # Remplir le reste avec des zéros si nécessaire

    write_command = [0xFF, 0xD6, 0x00, block_number, 0x10] + data_bytes
    try:
        response, sw1, sw2 = connection.transmit(write_command)
        if sw1 == 0x90 and sw2 == 0x00:
            return True
        else:
            print(f"Erreur lors de l'écriture dans le bloc {block_number} : {sw1:02X} {sw2:02X}")
            return False
    except NoCardException:
        print("Erreur : Aucune carte n'est présente sur le lecteur.")
        return False
    except CardConnectionException as e:
        print(f"Exception lors de l'écriture dans le bloc {block_number} : {e}")
        return False

def write_data_dynamically(connection, data, key):
    data_bytes = data.encode('utf-8')
    blocks_per_sector = 3  # Les secteurs réguliers ont 3 blocs de données
    total_blocks_needed = (len(data_bytes) + 15) // 16  # Nombre de blocs nécessaires

    sector = 3  # Commencer par le secteur 3 pour éviter les secteurs réservés
    block_offset = 0

    while total_blocks_needed > 0:
        if not authenticate_sector(connection, sector, key):
            print(f"Impossible d'authentifier le secteur {sector}.")
            return False

        # Écrire dans les blocs du secteur actuel
        for block in range(3):
            if total_blocks_needed == 0:
                break

            # Extraire les 16 octets de données à écrire dans le bloc
            block_data = data_bytes[block_offset:block_offset + 16]
            block_offset += 16
            total_blocks_needed -= 1

            global_block = sector * 4 + block
            print(f"Écriture dans le bloc {global_block} du secteur {sector}...")
            if not write_block(connection, global_block, block_data):
                print(f"Échec de l'écriture dans le bloc {global_block}.")
                return False

        # Passer au secteur suivant
        sector += 1

        # Si on dépasse le dernier secteur disponible
        if sector >= 16:
            print("Erreur : Pas assez de secteurs disponibles pour écrire toutes les données.")
            return False

    print(f"Données écrites avec succès sur {len(data_bytes)} octets répartis sur plusieurs secteurs.")
    return True

def read_card():
    try:
        available_readers = readers()
        if not available_readers:
            return {"error": "Aucun lecteur de carte n'a été trouvé. Veuillez brancher un lecteur."}

        reader = available_readers[0]
        connection = reader.createConnection()
        connection.connect()

        uid = get_uid(connection)
        atr = get_atr(connection)

        card_data = {
            "uid": uid,
            "atr": atr,
            "sectors": {}
        }

        key = [0xFF] * 6  # Clé par défaut pour l'authentification
        for sector in range(3, 16):  # On évite les secteurs 0, 1, et 2
            sector_data = read_sector_data(connection, sector, key)
            if sector_data:
                card_data["sectors"][sector] = sector_data

        return card_data

    except NoCardException:
        return {"error": "Aucune carte n'est détectée sur le lecteur."}
    except CardConnectionException as e:
        return {"error": f"Erreur de connexion au lecteur : {e}"}
    except Exception as e:
        return {"error": f"Erreur inconnue : {e}"}

def write_card(data):
    try:
        available_readers = readers()
        if not available_readers:
            return False, "Aucun lecteur de carte n'a été trouvé. Veuillez brancher un lecteur."

        reader = available_readers[0]
        connection = reader.createConnection()
        connection.connect()

        key = [0xFF] * 6  # Clé par défaut pour l'authentification
        success = write_data_dynamically(connection, data, key)

        return success, "Données écrites avec succès." if success else "Échec de l'écriture des données."

    except NoCardException:
        return False, "Aucune carte n'est détectée sur le lecteur."
    except CardConnectionException as e:
        return False, f"Erreur de connexion au lecteur : {e}"
    except Exception as e:
        return False, f"Erreur inconnue : {e}"