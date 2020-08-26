from fastapi import FastAPI

from app import db, settings, telegram
from app.routes import router

app = FastAPI(debug=settings.APP_DEBUG)
app.add_event_handler("startup", db.create_indexes)
app.include_router(router)

# telegram.use_with_debug(app)
