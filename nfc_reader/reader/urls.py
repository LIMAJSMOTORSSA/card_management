# urls.py

from django.urls import path
from .view import (
    add_user_view,
    add_card, card_list, change_security_key, format_card,
    card_info, passenger_card_database, subscription, transaction_database, user_database, user_systeme,
    home,
    qr_code, nfc,
    test_ecriture, test_lecture, test_transaction, login_view, logout_view, check_nfc_reader_status, api_dashboard_stats, user_detail,add_or_update_user, delete_user, create_transaction,  search_usersub, choose_payment_frequency, select_subscriptions, checkout,search_users_api,user_search_page, search_usernfc, card_assignment_page, get_card_assignments, create_card , process_nfc_scan, approve_boarding, send_database   
)



urlpatterns = [
    path('home', home, name='home'),
    path('send-database/', send_database, name='send_database'),
    path('api/nfc-status/', check_nfc_reader_status, name='nfc_status'),
    path('api/dashboard-stats/', api_dashboard_stats, name='api_dashboard_stats'),
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('add-user/', add_user_view, name='add_user'),  # Ajout d'utilisateur

    # Cartes
    path('add-card/', add_card, name='add_card'),
    path('card-list/', card_list, name='card_list'),
    path('card-info/', card_info, name='card_info'),  # Info carte spécifique
    path('change-security-key/', change_security_key, name='change_security_key'),
    path('format-card/', format_card, name='format_card'),

    # NFC et Scan
    path('nfc/', nfc, name='nfc'),
    
    path('process_nfc_scan/', process_nfc_scan, name='process_nfc_scan'),

    # URL pour approuver ou désapprouver l'embarquement
    path('approve_boarding/', approve_boarding, name='approve_boarding'),
    
    path('qr-code/', qr_code, name='qr_code'),  # QR code d'un utilisateur spécifique

    # Base de données
    path('passenger-card-database/', passenger_card_database, name='passenger_card_database'),
    path('subscription/', subscription, name='subscription'),
    path('transaction-database/', transaction_database, name='transaction_database'),
    path('api/create-transaction/', create_transaction, name='create_transaction'),
    path('user-database/', user_database, name='user_database'),
    path('api/users/<int:pk>/', user_detail, name='user_detail'),
    path('user-systeme/', user_systeme, name='user_systeme'),
    path('user-systeme/add_or_update/', add_or_update_user, name='add_or_update_user'),
    path('user-systeme/delete/<int:user_id>/', delete_user, name='delete_user'),

    # Tests
    path('test-ecriture/', test_ecriture, name='test_ecriture'),
    path('test-lecture/', test_lecture, name='test_lecture'),
    path('test-transaction/', test_transaction, name='test_transaction'),
    
    path('search-usersub/', search_usersub, name='search_usersub'),
    path('choose-payment-frequency/<int:user_id>/', choose_payment_frequency, name='choose_payment_frequency'),
    path('select-subscriptions/<int:user_id>/<str:frequency>/', select_subscriptions, name='select_subscriptions'),
    path('checkout/<int:user_id>/<str:plan_ids>/<str:payment_method>/', checkout, name='checkout'),
    path('api/search-users/', search_users_api, name='search_users_api'),
    # Ajoutez d'autres routes ici si nécessaire
    #NFC
    path('user_search_page/', user_search_page, name='user_search_page'),
    path('api/search-user/', search_usernfc, name='search_usernfc'),
    path('card-assignment/<int:user_id>/', card_assignment_page, name='card_assignment_page'),
    path('api/get-card-assignments/', get_card_assignments, name='get_card_assignments'),
    path('create-card/', create_card, name='create_card'),
    
]
