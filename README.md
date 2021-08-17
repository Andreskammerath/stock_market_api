# STOCK MARKET API  
This API was build with FastAPI, ElasticSearch and Postgres. It uses api_key to get information from it. You can try it up on:  
https://andres-stock-market-api.herokuapp.com/ 

## MOST IMPORTANT ENDPOINTS  
### /auth/new  
This endpoin is to get an api key. Make sure to pass a valid email domain. Example of request's body:  
    {
    "name": "Andrés",
    "last_name": "Kammerath",
    "mail_address": "andreskammerath@gmail.com"
    }  

### /symbol/{symbol_name}  
This endpoint gives info about last 30 days of any stock in the market.The Info includes open price, higher price, lower price, closing price and difference between current day closing price and previous day closing price.  

### To watch full documentation on the endpoints please visit:
https://andres-stock-market-api.herokuapp.com/docs