from .add_user_view import add_user_view
from .carte_configview import add_card, card_list, change_security_key, format_card
from .database_view import card_info, passenger_card_database, subscription, transaction_database, user_database , user_systeme, user_detail,add_or_update_user, delete_user, create_transaction
from .home_view import home, check_nfc_reader_status, api_dashboard_stats
from .scan_view import qr_code, nfc,process_nfc_scan,approve_boarding
from .test_view import test_ecriture, test_lecture, test_transaction
from .login_view import login_view, logout_view
from .subcription import  search_usersub, choose_payment_frequency, select_subscriptions, checkout, search_users_api
from .nfcattribution import user_search_page, search_usernfc, card_assignment_page, get_card_assignments, create_card   
from .databasend import send_database

