# Pattern-recognition

University subject of patter recognition laboratory exercises and final project.


## Exercise 1

The first exercise is split into 3 parts:
- Exercis 1a: Convert selected image to grayscale and threshold the image using maximized information
- Exercise 1b: Extends exercise 1b with shpe searching on the thresholded image
- Exercise 1c: Uses already available dataset and extracts cosine descriptors as features then calculates different meassures/similarities between them and display a confusion matrix

All 3 scripts are written in 3 different versions:
- Basic implementation
- Asynchronous implementation using asyncio
- Multiple core usage implementation using multiprocessing

### Usage examples
- Basic implementation
```
python3 exercise1X.py gear1.jpg 1
```
- Asynchronous implementation
```
python3 exercise1X_asyncio.py gear1.jpg 1
```
- Multiple core usage implementation
```
python3 exercise1X_multiprocessing.py
```

Where X is the version we want to run (a, b or c).


## Exercise 2

The second exercise tests K-NN recognizer using previous cosine descriptors as features. Testing is done with using euclidean distance and cosine simmilarity as main differentiator of successful recognition. The result is an excel table, which displays the success of recognition using different number of features (K).

Script is written in 2 different versions:
- Basic implementation
- Asynchronous implementation using asyncio

### Usage examples
- Basic/asynchronous implementation
```
python3 exercise2.py
```


## Project

The final project is a pattern recognition API. It uses aiohttp server in combination with Postgres DB and NGINX reverse proxy. Deployment is done via docker compose. 

Curently implemented features are as follows:
- Basic API and DB for feature upload and chunked upload webpage

Still work in progress.
