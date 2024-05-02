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

The final project is a pattern recognition API for exploratory data analysis. More information can be found in the respective README file in the Project folder.

The project is still in development and is not yet finished...

Curent roadmap:
- [x] Create a basic API for feature set creation/deletion
- [x] Create a basic API for exploratory data analysis using PCA and hierarchical clustering
- [x] Create a basic nginx reverse proxy for the frontend and backend
- [x] Create a basic wrapper for various web requests done from the frontend
- [x] Deploy the project using docker compose
- [ ] Create a basic frontend for the API
- [ ] Add more features to the API
- [ ] Add more features to the frontend
- [ ] Deploy the project using Kubernetes
    - [ ] Add a DB k8s deployment
    - [ ] Add a API k8s deployment
    - [ ] Add a frontend k8s deployment