# StormsNStocks
CS5246 Group Project

## Env
```
pyenv install 3.10
pyenv local 3.10

poetry env use 3.10
poetry intsall

poetry run pip3 install news-please
```

## Data
### Disaster Data
- US natural disaster from 2019 to 2023
- source: https://en.wikipedia.org/wiki/List_of_natural_disasters_in_the_United_States
- 11 types of disaster:
    - earthquake
    - hurricane
    - tropical storm
    - wildfire
    - derecho
    - winter storm
    - flood
    - heat wave
    - tornado
    - bomb cyclone
    - blizzard

### News
- the guardian API: https://open-platform.theguardian.com/documentation/

- How to download news data
```
# create data folder
mkdir -p data/news

# query the Guardian news from 2019 to 2023
poetry run python -m src.news_collector --api_key <YOUR_API_KEY> --start_year 2019 --start_year 2023 --path_prefix /data/news
```
