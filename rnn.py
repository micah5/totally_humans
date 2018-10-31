__author__  = "Micah Price"
__email__   = "98mprice@gmail.com"

from argparse import ArgumentParser

from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.utils.data_utils import get_file
from keras.optimizers import RMSprop

import numpy as np
import random
import sys
import os
import io

name = 'titles'

with io.open('data/%s.txt' % name, encoding='utf-8') as f:
    text = f.read()

print('corpus length:', len(text))

words = set(text.split())
#print('unique', words)
words = sorted(words)
#print('sorted', words)
'''for i in range(len(words)):
    print("%i:%s" % (i, words[i]))'''

print("words",type(words))
print("total number of unique words",len(words))

word_indices = dict((c, i) for i, c in enumerate(words))
indices_word = dict((i, c) for i, c in enumerate(words))

print("word_indices", type(word_indices), "length:",len(word_indices) )
print("indices_words", type(indices_word), "length", len(indices_word))

maxlen = 30
step = 3
print("maxlen:",maxlen,"step:", step)
sentences = []
next_words = []
sentences1 = []
list_words = []

sentences2=[]
list_words=text.split()
print('list_words', type(list_words), len(list_words))

for i in range(0,len(list_words)-maxlen, step):
    sentences2 = ' '.join(list_words[i: i + maxlen])
    sentences.append(sentences2)
    next_words.append((list_words[i + maxlen]))
print('nb sequences(length of sentences):', len(sentences))
print("length of next_word",len(next_words))

print('Vectorization...')
X = np.zeros((len(sentences), maxlen, len(words)), dtype=np.bool)
print('X shape', X.shape)
y = np.zeros((len(sentences), len(words)), dtype=np.bool)
print('y shape', y.shape)
for i, sentence in enumerate(sentences):
    #print('%d: %s' % (i, sentence))
    for t, word in enumerate(sentence.split()):
        #print('setting (%d, %d, %d) to 1' % (i, t, word_indices[word]))
        X[i, t, word_indices[word]] = 1
    y[i, word_indices[next_words[i]]] = 1

#build the model: 2 stacked LSTM
print('Build model...')
print('maxlen', maxlen, 'len(words)', len(words))
model = Sequential()
model.add(LSTM(128, return_sequences=True, input_shape=(maxlen, len(words))))
model.add(Dropout(0.2))
model.add(LSTM(128, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(len(words)))
model.add(Activation('softmax'))

model.compile(loss='categorical_crossentropy', optimizer=RMSprop(lr=0.002))

model.fit(X, y, batch_size=32, nb_epoch=50)
model.save('/output/%s.h5' % name)

def sample(a, temperature=1.0):
    # helper function to sample an index from a probability array
    a = np.log(a) / temperature
    dist = np.exp(a)/np.sum(np.exp(a))
    choices = range(len(a))
    return np.random.choice(choices, p=dist)

start_index = random.randint(0, len(list_words) - maxlen - 1)

diversity = 0.5
print()
print('----- diversity:', diversity)
generated = ''
sentence = list_words[start_index: start_index + maxlen]
generated += ' '.join(sentence)
print('----- Generating with seed: "' , sentence , '"')
print()
sys.stdout.write(generated)
print()

for i in range(100):
    x = np.zeros((1, maxlen, len(words)))
    for t, word in enumerate(sentence):
        x[0, t, word_indices[word]] = 1.
    preds = model.predict(x, verbose=0)[0]
    next_index = sample(preds, diversity)
    next_word = indices_word[next_index]
    generated += next_word
    del sentence[0]
    sentence.append(next_word)
    sys.stdout.write(' ')
    sys.stdout.write(next_word)
    sys.stdout.flush()
print()
