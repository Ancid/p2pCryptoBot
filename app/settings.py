import os


APP_NAME = "paxful-offers-bot"
TOKEN = '1206885593:AAH4kKVpyM-BdznBGmaHmriMfoF2PR49sBc'    #prod
MONGODB_URI = os.environ["MONGODB_URI"]
APP_DEBUG = os.environ.get("DEBUG", False)
# TOKEN = "1275378588:AAF3KRJxWTCsR5RXtG4H6WRkybr4Gkk-g3Y"  # test
# MONGODB_URI = 'mongodb://localhost:27017/offersBot'
# APP_DEBUG = os.environ.get("DEBUG", True)

DB_NAME = "db/offersStorage"
API_KEY = "Z4TPCz2VKHTlRAMAXxLqgHS18MT7eLbd"
API_SECRET = b"tdlPtrDbSM8jacK1I3VPNwNx7svXkaL0"
SEARCH_LIMIT = 5
SUBSCRIPTION_LIMIT = 10
OFFERS_DAYS_FILTER = 5
MODE_SEARCH = "search"
MODE_SUBSCRIBE = "subscription"
WEBAPP_PORT = int(os.environ.get('PORT', 5000))
WEBHOOK_HOST = f"https://{APP_NAME}.herokuapp.com/"
WEBHOOK_URL = f"{WEBHOOK_HOST}{TOKEN}"
