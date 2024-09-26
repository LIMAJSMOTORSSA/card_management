from smartcard.System import readers
from smartcard.Exceptions import CardConnectionException, NoCardException

def authenticate_sector(connection, sector_number, key):
    sector_trailer_block = sector_number * 4 + 3
    load_key_command = [0xFF, 0x82, 0x00, 0x00, 0x06] + key
    authenticate_command = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, sector_trailer_block, 0x60, 0x00]
    
    try:
        connection.transmit(load_key_command)
        response, sw1, sw2 = connection.transmit(authenticate_command)
        return sw1 == 0x90 and sw2 == 0x00
    except (CardConnectionException, NoCardException):
        return False

def read_block(connection, block_number):
    read_command = [0xFF, 0xB0, 0x00, block_number, 0x10]
    try:
        response, sw1, sw2 = connection.transmit(read_command)
        if sw1 == 0x90 and sw2 == 0x00:
            return response
        return None
    except (CardConnectionException, NoCardException):
        return None

def read_sector_12():
    try:
        r = readers()
        if len(r) < 1:
            return ""

        connection = r[0].createConnection()
        connection.connect()

        SECTOR = 12
        BLOCK = 48
        KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]  # Clé par défaut

        if authenticate_sector(connection, SECTOR, KEY):
            block_data = read_block(connection, BLOCK)
            if block_data:
                ascii_data = ''.join([chr(b) if 32 <= b <= 126 else '' for b in block_data])
                return ascii_data.strip()
        
        return ""

    except Exception:
        return ""
    finally:
        if 'connection' in locals():
            connection.disconnect()

# Exemple d'utilisation
if __name__ == "__main__":
    result = read_sector_12()
    print(result)