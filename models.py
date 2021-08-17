from dateutil.parser import parse as date_parser
from elasticsearch_dsl import (
    Document,
    Date,
    Integer,
    Keyword,
    Text,
    InnerDoc,
    Object,
    Nested,
    Boolean,
    Float,
)
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.query import Match, Term
import collections
import os
import requests


connections.create_connection(hosts=[os.getenv('ELASTIC_HOST')])

class Stock(Document):
    stock_symbol = Keyword()
    open_price = Float()
    lower_price = Float()
    higher_price = Float()
    close_price = Float()
    date = Date()

    class Index:
        name = "stock_info"

    def to_json(self, prev_closing_price):
        return {
            'symbol': self.stock_symbol,
            'open_price': self.open_price,
            'lower_price': self.lower_price,
            'higher_price': self.higher_price,
            'close_price': self.close_price,
            'day': self.date,
            'difference_closing_price': self.close_price - prev_closing_price
        }

    @classmethod
    def symbol_info(cls, symbol):
        ss = list(Stock.search().filter(Term(stock_symbol=symbol)).filter(
                'range', date={'gte': 'now-50d', 'lt': 'now'}).sort('-date').scan())
        if not ss:
            Stock.add_new_symbol(symbol)
            ss = list(Stock.search().filter(Term(stock_symbol=symbol)).filter(
                    'range', date={'gte': 'now-50d', 'lt': 'now'}).sort('-date').scan())
            if not ss:
                return
        last_31_elements = [ss[i].to_json(ss[i+1]['close_price']) for i in range(31)]
        response = collections.defaultdict(dict)
        for e in last_31_elements:
            response[e['day']] = e
        return dict(response)
        

    @classmethod
    def add_new_symbol(cls, symbol):
        url = (
            f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}"
            f"&outputsize=compact&apikey=X86NOH6II01P7R24")
        r = requests.get(url)
        data = r.json()
        if 'Error Message' in data:
            return
        for day, info in data.get('Time Series (Daily)').items():
            cls(
                stock_symbol=symbol,
                open_price=info.get('1. open', None),
                lower_price=info.get('3. low', None),
                higher_price=info.get('2. high', None),
                close_price=info.get('4. close', None),
                date=date_parser(day)
            ).save()
    # TODO method to update db
        

