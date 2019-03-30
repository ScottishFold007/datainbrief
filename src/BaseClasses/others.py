import pandas as pd
from bs4 import BeautifulSoup
from requests import get

def pandas():
    tables = pd.read_html("https://www.imdb.com/chart/moviemeter?ref_=nv_mv_mpm", header=0)

    print(tables[0])
def b4():


    url = 'https://www.sahibinden.com'

    response = get(url)
    print(response)
    print(response.text[:100])