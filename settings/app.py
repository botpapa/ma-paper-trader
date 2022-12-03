"""
Setting up fastapi app
"""
import fastapi
from fastapi.middleware.cors import CORSMiddleware


app = fastapi.FastAPI(
    title='Binance Paper Trading API',
    docs=None,
    redoc=None
)

# Setting up CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
