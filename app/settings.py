from starlette.config import Config

config = Config(".env")

# os.environ['MONGODB_URI'] = 'mongodb://localhost:27017/offersBot'
TOKEN = "1275378588:AAF3KRJxWTCsR5RXtG4H6WRkybr4Gkk-g3Y"  # test

APP_NAME = "paxful-offers-bot"
APP_DEBUG = config.get("DEBUG", cast=bool, default=False)

API_KEY = "Z4TPCz2VKHTlRAMAXxLqgHS18MT7eLbd"
API_SECRET = b"tdlPtrDbSM8jacK1I3VPNwNx7svXkaL0"
SEARCH_LIMIT = 5
SUBSCRIPTION_LIMIT = 10
OFFERS_DAYS_FILTER = 5
MODE_SEARCH = "search"
MODE_SUBSCRIBE = "subscription"
