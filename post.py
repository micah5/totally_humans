__author__  = "Micah Price"
__email__   = "98mprice@gmail.com"

import config

from keras.models import Sequential, load_model
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.utils.data_utils import get_file
from keras.optimizers import RMSprop

import praw
import numpy as np
import random
import sys
import os
import io

def sample(a, temperature=1.0):
    # helper function to sample an index from a probability array
    a = np.log(a) / temperature
    dist = np.exp(a)/np.sum(np.exp(a))
    choices = range(len(a))
    return np.random.choice(choices, p=dist)

with io.open('data/comments.txt', encoding='utf-8') as f:
    comment_text = f.read()

comment_words = set(comment_text.split())
comment_words = sorted(comment_words)

comment_word_indices = dict((c, i) for i, c in enumerate(comment_words))
comment_indices_word = dict((i, c) for i, c in enumerate(comment_words))

maxlen = 30
comment_list_words=comment_text.split()

comment_model = load_model('models/comments.h5')

with io.open('data/titles.txt', encoding='utf-8') as f:
    title_text = f.read()

title_words = set(title_text.split())
title_words = sorted(title_words)

title_word_indices = dict((c, i) for i, c in enumerate(title_words))
title_indices_word = dict((i, c) for i, c in enumerate(title_words))

title_list_words=title_text.split()

title_model = load_model('models/titles.h5')

def generate_comments():
    start_index = random.randint(0, len(comment_list_words) - maxlen - 1)

    diversity = 0.5
    sentence = comment_list_words[start_index: start_index + maxlen]
    generated = ' '.join(sentence)

    comments = []
    str = ''
    for i in range(100):
        x = np.zeros((1, maxlen, len(comment_words)))
        for t, word in enumerate(sentence):
            x[0, t, comment_word_indices[word]] = 1.
        preds = comment_model.predict(x, verbose=0)[0]
        next_index = sample(preds, diversity)
        next_word = comment_indices_word[next_index]
        generated += next_word
        del sentence[0]
        sentence.append(next_word)
        if next_word == '<break>':
            comments.append(str)
            str = ''
        else:
            str += ' '
            str += next_word.upper()
    return comments

def generate_title():
    start_index = random.randint(0, len(title_list_words) - maxlen - 1)

    diversity = 0.5
    sentence = title_list_words[start_index: start_index + maxlen]
    generated = ' '.join(sentence)

    str = ''
    for i in range(100):
        x = np.zeros((1, maxlen, len(title_words)))
        for t, word in enumerate(sentence):
            x[0, t, title_word_indices[word]] = 1.
        preds = title_model.predict(x, verbose=0)[0]
        next_index = sample(preds, diversity)
        next_word = title_indices_word[next_index]
        generated += next_word
        del sentence[0]
        sentence.append(next_word)
        if next_word == '<break>':
            if i >= 2:
                break
        else:
            str += ' '
            str += next_word.upper()
    if len(str) >= 300:
        str = str[0:300]
    return str

reddit = praw.Reddit(client_id=config.client_id,
                     client_secret=config.client_secret,
                     user_agent=config.user_agent,
                     username=config.username,
                     password=config.password)

def get_random_submission():
    id = reddit.subreddit('totallynotrobots').random()
    submission = praw.models.Submission(reddit, id)
    return submission.url

def post_to_reddit():
    print(reddit.user.me())
    submission = reddit.subreddit('totally_humans').submit(title=generate_title(), url=get_random_submission())
    comment_chain = generate_comments()
    comment = submission.reply(comment_chain[0])
    for comment_str in comment_chain[1:]:
        comment = comment.reply(comment_str)

post_to_reddit()
