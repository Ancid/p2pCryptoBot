import os

# os.environ['MONGODB_URI'] = 'mongodb://localhost:27017/offersBot'
# os.environ['DEBUG'] = 'True'
TOKEN = '1275378588:AAF3KRJxWTCsR5RXtG4H6WRkybr4Gkk-g3Y'  # test
# TOKEN = '1206885593:AAH4kKVpyM-BdznBGmaHmriMfoF2PR49sBc'    #prod

# mongodb://heroku_7xn6mnj8:ge4vafiitl2sndi792toil40lt@ds121251.mlab.com:21251/heroku_7xn6mnj8?retryWrites=false
# os.environ['MONGODB_URI'] = 'mongodb://paxbot-user:56ogVp8kncjxwtpK@cluster0-shard-00-00.qk51l.mongodb.net:27017,cluster0-shard-00-01.qk51l.mongodb.net:27017,cluster0-shard-00-02.qk51l.mongodb.net:27017/heroku_7xn6mnj8?ssl=true&replicaSet=atlas-6kx4i6-shard-0&authSource=admin&w=majority'
# os.environ['MONGODB_ATLAS'] = 'mongodb+srv://paxbot-user:56ogVp8kncjxwtpK@cluster0.afujh.mongodb.net/paxbot'
# os.environ['MONGODB_URI_NEW'] = 'mongodb://paxbot-user:56ogVp8kncjxwtpK@cluster0-shard-00-02.afujh.mongodb.net/paxbot'
APP_NAME = 'webhook-test-bot'
API_KEY = "Z4TPCz2VKHTlRAMAXxLqgHS18MT7eLbd"
API_SECRET = b"tdlPtrDbSM8jacK1I3VPNwNx7svXkaL0"
SEARCH_LIMIT = 5
SUBSCRIPTION_LIMIT = 10
OFFERS_DAYS_FILTER = 5
MODE_SEARCH = 'search'
MODE_SUBSCRIBE = 'subscription'
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.environ.get('PORT', 5000))
WEBHOOK_HOST = f"https://{APP_NAME}.herokuapp.com/"
WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
