# app/core/__init__.py

from fastapi.security import OAuth2PasswordBearer

# FastAPI tarafında security dependency olarak kullanacağız
# DİKKAT: tokenUrl mutlaka gerçek login endpoint'i ile aynı olmalı.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",  # <- ÖNEMLİ KISIM
    scheme_name="OAuth2PasswordBearer",
)
