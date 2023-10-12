import json
import logging
import datetime

logging.basicConfig(filename='logging/main.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_banned(update, context):
    user_id = update.effective_chat.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open('data/banned_users.json', 'r') as f:
            banned_users = json.load(f)
            banned_user_ids = [str(user['user_id']) for user in banned_users['banned_users']]
            
            if str(user_id) in banned_user_ids:
                logging.warning(f"Utilisateur {user_id} est dans la liste des bannis.")
                
                # Enregistrer la tentative de connexion dans un fichier JSON
                with open('logging/ban_manager.log', 'a') as log_f:
                    log_data = {
                        'user_id': user_id,
                        'username': username,
                        'first_name': first_name,
                        'last_name': last_name,
                        'timestamp': timestamp,
                        'action': 'Tentative de connexion'
                    }
                    json.dump(log_data, log_f)
                    log_f.write('\n')

                return True, [user for user in banned_users['banned_users'] if str(user['user_id']) == str(user_id)][0]['reason']
            
        logging.info(f"Utilisateur {user_id} n'est pas dans la liste des bannis.")
        return False, None

    except Exception as e:
        logging.error(f"Erreur dans is_banned : {e}")
        return False, None
