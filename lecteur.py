from smartcard.System import readers
from smartcard.Exceptions import NoCardException

def get_reader_names():
    try:
        reader_list = readers()
        if not reader_list:
            print("Aucun lecteur détecté.")
            return

        print("Lecteurs détectés :")
        for reader in reader_list:
            try:
                connection = reader.createConnection()
                connection.connect()
                if "ACR122U" in reader.name:
                    print(f"- {reader.name}")  # Affiche le nom complet, y compris "ACS ACR122U PICC"
                else:
                    print(f"- {reader.name}")
                connection.disconnect()
            except NoCardException:
                # Carte non présente, on affiche quand même le nom du lecteur
                print(f"- {reader.name} (Pas de carte détectée)")
            except Exception as e:
                # Autres exceptions potentielles
                print(f"- {reader.name} (Erreur: {str(e)})")

    except Exception as e:
        print(f"Erreur lors de la détection des lecteurs : {str(e)}")

if __name__ == "__main__":
    get_reader_names()