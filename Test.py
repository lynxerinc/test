import requests

JSONBIN_URL = 'https://api.jsonbin.io/b/64e54c3a8e4aa6225ed3f094'
JSONBIN_SECRET_KEY = '$2b$10$L0HWphq9OuQfMZ9Ryl70tOUn/TwsXy0zfuFbFUkdvphhQ3LdpeJlW'
HEADERS = {
    'Content-Type': 'application/json',
    'secret-key': JSONBIN_SECRET_KEY,
}

# Exemple de données à sauvegarder
data_to_save = {
    'name': 'John Doe',
    'age': 30,
    'city': 'Paris'
}

# Sauvegarde des données dans le bin
response = requests.put(JSONBIN_URL, json=data_to_save, headers=HEADERS)
if response.status_code == 200:
    print("Données sauvegardées avec succès.")
else:
    print("Erreur lors de la sauvegarde des données.")

# Récupération des données depuis le bin
response = requests.get(JSONBIN_URL, headers=HEADERS)
if response.status_code == 200:
    data_retrieved = response.json()
    print("Données récupérées avec succès :", data_retrieved)
else:
    print("Erreur lors de la récupération des données.")
