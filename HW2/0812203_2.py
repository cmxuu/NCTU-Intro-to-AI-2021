# -*- coding: utf-8 -*-
"""0812203_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JSCiSh38NuYEMDYuizO88JlAI2ENa3Mh
"""

###########################
# DO NOT CHANGE THIS CELL #
###########################

import os
import urllib.request
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import f1_score, accuracy_score


def load_dataset(url):
  """ Get and load weather dataset. """

  path = url.split('/')[-1] # get the file name from url

  if not os.path.exists(path):
    print('Download:', url)
    urllib.request.urlretrieve(url, path)

  return pd.read_pickle(path) # pickle protocol=4


def get_input_target(df):
  """ Get X and y from weather dataset. """
  
  target_column = 'RainTomorrow' # predict 1 of it rains tomorrow

  X = df.drop(columns=[target_column]).to_numpy()
  y = df[target_column].to_numpy()

  return X, y


def k_fold_cv(model_create_fn, X, y, k=5):
  """ Run k-fold cross-validation. """

  results = []

  idxs = list(range(X.shape[0]))
  np.random.shuffle(idxs)
  X, y = X[idxs], y[idxs]

  for i, (train_idxs, val_idxs) in enumerate(KFold(k).split(idxs)):
    splits = {'train': (X[train_idxs], y[train_idxs]),
              'val':   (X[val_idxs],   y[val_idxs]  )}

    print('Run {}:'.format(i+1))

    model = model_create_fn()
    model.fit(*splits['train']) # training

    for name, (X_split, y_split) in splits.items():
      y_pred = model.predict(X_split)

      result = {'split': name,
                'f1': f1_score(y_pred, y_split),
                'acc': accuracy_score(y_pred, y_split)}
      results.append(result)

      print('{split:>8s}: f1={f1:.4f} acc={acc:.4f}'.format(**result))

  return pd.DataFrame(results)


# begin

# TODO: you can define or import something here (optional)

import random
import collections

class Model:

  def __init__(self, num_features: int, num_classes: int):

    # num_features (int) : the input feature size.
    # num_classes (int) : number of output classes.
    self.num_features = num_features
    self.num_classes = num_classes
    self.numTree = 5
    self.maxDepth = 10
    self.trees = None


  def fit(self, X: np.ndarray, y: np.ndarray):

    # generate forest
    self.trees = []
    for i in range(self.numTree):
      np.random.seed(i)
      split = random.sample(range(np.size(X, 0)), int(np.size(X, 0)*0.1))
      subX= X[split, :]
      subY = y[split]
      tree = self.buildTree(subX, subY, 0)
      self.trees += [tree]


  def predict(self, X: np.ndarray) -> np.ndarray:
    
    # find pred value
    temp = []
    for tree in self.trees:
      tt = []
      for x in X:
        tt += [tree.predict(x)]
      temp += [tt]

    # choose the closest value
    pred = np.array(temp).T.tolist()
    q = []
    for yy in pred:
      q += [np.argmax(np.bincount(yy))]
    return np.array(q)


  def buildTree(self, X, y, depth):

    # check num of samples and classes
    if (len(np.unique(y))<= 1 or np.size(X, 0) <= 100):
      tree = Tree()
      tree.group = np.argmax(np.bincount(y))
      return tree

    if depth < self.maxDepth:

      # find split value
      spFeature = None
      spThreshold = None
      gain = 1
      for i in range(np.size(X, 1)):
        threshold = np.unique(X[:, i]).tolist()
        for th in threshold:
          y2 = y[X[:, i] <= th]
          y3 = y[X[:, i] > th]
          p2 = np.sum(y2)/(len(y2)+1)
          p3 = np.sum(y3)/(len(y3)+1)
          gainTmp = (1-np.sum(p2**2)-(1-p2)**2)*len(y2)/(len(y2)+len(y3)) + (1-np.sum(p3**2)-(1-p3)**2)*len(y3)/(len(y2)+len(y3))
          if gainTmp < gain:
            spFeature = i
            spThreshold = th
            gain = gainTmp
            
      # split 
      geThreshold = X[:, spFeature] <= spThreshold
      Xtrain, yTrain = X[geThreshold], y[geThreshold]
      Xval, yVal = X[~geThreshold], y[~geThreshold]
      tree = Tree()

      if (np.size(Xtrain, 0) <= 10 or np.size(Xval, 0) <= 10 or gain <= 0.01):
        tree.group = np.argmax(np.bincount(y))
        return tree
      else:
        tree.spFeature = spFeature
        tree.spThreshold = spThreshold
        tree.left = self.buildTree(Xtrain, yTrain, depth+1)
        tree.right = self.buildTree(Xval, yVal, depth+1)
        return tree

    else:
      tree = Tree()
      tree.group = np.argmax(np.bincount(y))
      return tree

class Tree():

  def __init__(self):
    self.spFeature = None
    self.spThreshold = None
    self.group = None
    self.left = None
    self.right = None

  def predict(self, X):
    if self.group is not None:
      return self.group
    elif X[self.spFeature] < self.spThreshold:
      return self.left.predict(X)
    else:
      return self.right.predict(X)

# end

###########################
# DO NOT CHANGE THIS CELL #
###########################

df = load_dataset('https://lab.djosix.com/weather.pkl')
X_train, y_train = get_input_target(df)

df.head()

###########################
# DO NOT CHANGE THIS CELL #
###########################

create_model = lambda: Model(X_train.shape[1], 2)
k_fold_cv(create_model, X_train, y_train).groupby('split').mean()