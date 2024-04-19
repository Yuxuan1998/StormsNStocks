# StormsNStocks
CS5246 Group Project

## Enviroment Setup
```
pyenv install 3.10
pyenv local 3.10

poetry env use 3.10
poetry intsall

poetry run pip3 install news-please
poetry run pip3 install catboost
```

## Data
### News

All downloaded news data are saved in `data/news.zip`

- Before running the `news_collector` please register an access key for guardian API: https://open-platform.theguardian.com/documentation/

- How to download news data
```
# create data folder
mkdir -p data/news

# query the Guardian news from 2019 to 2023
poetry run python -m src.news_collector --api_key <YOUR_API_KEY> --start_year 2019 --end_year 2023 --path_prefix data/news/
```
