from app.databases.db import get_db
from fastapi import Depends

# Database sesseion dependency

session = Depends(get_db)
