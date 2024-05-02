# Python Recognition-API

The python Recognition-API is composed of the following files and directories:
- **Dockerfile** - Multistage docker build for the API using poetry for package management
- **pyproject.toml** - Configuration file for python packages required for the API to run
- **recognitionapi** - Python module/Folder containing the API runtime and its submodules
    - __init.py__ - Initialization script that is required to define the Python module (Empty)
    - __main.py__ - Main script that handles the overview of API methods available
    - __dal__ - Data Access Layer (Python submodule/Sub-folder) that handles the interaction with the Postgres database
    - __model__ - Databse model (Python submodule/Sub-folder) definition using a multi-relational model to represent Feature sets and its Feature vectors
    - __typical_test_cases.txt__ - File including all the available methods we can call on the API. Used for manual testing and development
- **tests** - Python module/Folder containing the tests cases for both modules used in the API and the API its-self
    - __test_main.py__ - Test script for the main.py from recognition_api folder
    - __test_dal.py__ - Test script for the dal.py from recognition_api/dal folder
    - __test_model.py__ - Test script for the model.py from recognition_api/model folder

## API Overview

The API supports creation and modification of **numerical feature sets**. 

A feature set is a collection of feature vectors, where each feature vector is a list of numerical values and should be associated with a label, therefore the limitation of the API is that the last value in the feature vector should be a __string__ label and the feature vectors should be comma sepparated __float__ values of the same length. Bellow is an example of a feature set with 3 feature vectors:
```json
{
    "FeatureSet": "iris",
    "Features": [
        "5.1, 3.5, 1.4, 0.2, Iris-setosa",
        "5.0, 3.5, 1.6, 0.6, Iris-setosa",
        "4.3, 3.0, 1.1, 0.1, Iris-setosa"
    ]
}
```

The API is a RESTful API that provides the following methods:
- **GET /recognition-api/v1/healthz** - Health check endpoint
```bash
curl -request GET http://localhost:5000/recognition-api/v1/healthz
```
- **POST /recognition-api/v1/uploadFeatureSet** - Upload a feature set to the database
```bash
curl --request POST --header "Content-Type: application/json" --data '{"FeatureSet": "iris", "Features": ["5.1,3.5,1.4,0.2,Iris-setosa", "5.0,3.5,1.6,0.6,Iris-setosa", "4.3,3.0,1.1,0.1,Iris-setosa"]}' http://127.0.0.1:5000/recognition-api/v1/uploadFeatureSet 
```
- **POST /recognition-api/v1/extendFeatureSet** - Extend a feature set in the database
```bash
curl --request POST --header "Content-Type: application/json" --data '{"FeatureSet": "iris", "Features": ["5.7,2.6,3.5,1.0,Iris-versicolor", "5.9,3.0,5.1,1.8,Iris-virginica"]}' http://127.0.0.1:5000/recognition-api/v1/extendFeatureSet
```
- **DELETE /recognition-api/v1/deleteFeatureSet** - Delete a feature set from the database
```bash
curl --request DELETE --header "Content-Type: application/json" --data '{"FeatureSet": "iris"}' http://127.0.0.1:5000/recognition-api/v1/deleteFeatureSet
```
- **GET /recognition-api/v1/getListOfFeatureSets** - Get a feature set from the database
```bash
curl -request GET http://localhost:5000/recognition-api/v1/getListOfFeatureSets
```
- **GET /recognition-api/v1/principalComponentAnalysis** - Perform PCA on a feature set from the database using the number of components specified
```bash
curl --request GET --header "Content-Type: application/json" --data '{"FeatureSet": "iris", "NumOfComponents": 2}' http://127.0.0.1:5000/recognition-api/v1/principalComponentAnalysis
```
- **GET /recognition-api/v1/optimizedPrincipalComponentAnalysis** - Perform PCA on a feature set from the database using all variation of components and return the best one based on the requested variance (If the requested variance is not found, the API will return the PCA with the highest variance)
```bash
curl --request GET --header "Content-Type: application/json" --data '{"FeatureSet": "iris", "RequestedVariance": 0.95}' http://127.0.0.1:5000/recognition-api/v1/optimizedPrincipalComponentAnalysis
```
- **GET /recognition-api/v1/hierarhicalClustering** - Perform Hierarchical Clustering on a feature set from the database using the number of clusters, metric and linkage method specified
```bash
curl --request GET --header "Content-Type: application/json" --data '{"FeatureSet": "iris", "Metric": "euclidean", "NumOfClusters": 2, "Linkage": "average"}' http://127.0.0.1:5000/recognition-api/v1/hierarhicalClustering
```
