from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException, CardConnectionException

def update_nfc_security_key(new_key):
    try:
        # Obtenir la liste des lecteurs
        reader_list = readers()
        if not reader_list:
            return {'status': 'error', 'message': 'Aucun lecteur de carte trouvé.'}
        
        reader = reader_list[0]
        connection = reader.createConnection()
        connection.connect()

        # Clé par défaut pour l'authentification (6 octets de FF)
        DEFAULT_KEY = [0xFF] * 6

        # Convertir la nouvelle clé en liste d'octets
        new_key_list = list(new_key)

        # Parcourir tous les secteurs de la carte (16 pour MIFARE Classic 1K)
        for sector in range(16):
            block = sector * 4 + 3  # Bloc de clé de chaque secteur

            # Authentification avec la clé par défaut
            auth_command = [0xFF, 0x86, 0x00, 0x00, 0x05,
                            0x01,  # Nombre de clés
                            0x00,  # MSB de l'adresse du bloc
                            block,  # LSB de l'adresse du bloc
                            0x60,  # Type de clé A
                            0x00]  # Emplacement de la clé (0x00 pour clé par défaut)

            data, sw1, sw2 = connection.transmit(auth_command + DEFAULT_KEY)
            if sw1 != 0x90:
                return {'status': 'error', 'message': f'Échec de l\'authentification sur le secteur {sector}.'}

            # Écrire la nouvelle clé dans le bloc de clé
            # Le bloc de clé contient : [Key A (6 octets), Access Bits (4 octets), Key B (6 octets)]
            # Nous allons remplacer Key A et Key B par la nouvelle clé
            access_bits = [0xFF, 0x07, 0x80, 0x69]  # Valeurs par défaut des bits d'accès
            new_block = list(new_key) + access_bits + list(new_key)

            write_command = [0xFF, 0xD6, 0x00, block, 0x10] + new_block
            data, sw1, sw2 = connection.transmit(write_command)
            if sw1 != 0x90:
                return {'status': 'error', 'message': f'Échec de la mise à jour de la clé sur le secteur {sector}.'}

        connection.disconnect()
        return {'status': 'success'}
    except NoCardException:
        return {'status': 'error', 'message': 'Aucune carte n\'est présente sur le lecteur.'}
    except CardConnectionException as e:
        return {'status': 'error', 'message': f'Erreur de connexion avec la carte : {str(e)}'}
    except Exception as e:
        return {'status': 'error', 'message': f'Erreur inattendue : {str(e)}'}
