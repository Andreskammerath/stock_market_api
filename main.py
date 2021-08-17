from fastapi import Depends, FastAPI, HTTPException, status
from fastapi_simple_security import api_key_router, api_key_security
from models import Stock

app = FastAPI()

app.include_router(api_key_router, prefix="/auth", tags=["_auth"])

@app.get("/")
async def root():
    return {"message": "Hi, welcome to Andres API"}

@app.get("/secure", dependencies=[Depends(api_key_security)])
async def secure():
    return {"message": "Hi, you are successfully authenticated"}

@app.get("/symbol/{symbol}", dependencies=[Depends(api_key_security)])
async def symbol_info(symbol: str):
    response = Stock.symbol_info(symbol)
    print(symbol)
    if not response:
        raise HTTPException(
            satus_code=404,
            detail="Stock symbol was not found."
        )
    else:
        return response
