# totally_humans
neural network trained on r/totallynotrobots

i.e. robots pretending to be humans pretending to be robots pretending to be humans

see results at https://www.reddit.com/r/totally_humans/

## requirements
- keras
- praw
- numpy

## config parameters
add your reddit auth to a file `config.py`, with these variables:
```python
client_id=''
client_secret=''
user_agent=''
username=''
password=''
```

## scrape data
PRAW can only scrape a max of 1000 of the most recent posts. this script iterates through all the titles & comments of each post and all data will be saved to `data` dir
```python
python extract_data.py
```

## train
just update the `name` variable in `rnn.py` before running to the name of your dataset (i.e. either 'comments' or 'titles')
```python
python rnn.py
```

## predict & post
```python
python post.py
```
