import os

import uvicorn

from app.main import app

if __name__ == '__main__':
    uvicorn.run(app, port=int(os.environ.get('PORT', 5000)))
