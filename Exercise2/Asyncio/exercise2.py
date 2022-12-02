import os, pandas, asyncio

from concurrent.futures import ProcessPoolExecutor
from csmknn_asyncio import *


async def exercise2_csmknn():
    # Set directory and root filename
    directory = "Pictures/"
    rootFilename = "obj"

    # If files with features and notes already exist we use them otherwise they are calculated
    if "X.npy" in os.listdir(".") and "y.npy" in os.listdir("."):
        #X, y = loadFeatures()
        X, y = await saveFeatures(directory, rootFilename)
    else:
        X, y = await saveFeatures(directory, rootFilename)

    # Check success of recognition for all combinations of 
    # number of features and number of nearest neighbours with euclidean distance
    resultsEUC = []
    for NFeatures in range(1, 25):
        if NFeatures == 24:
            NFeatures = "all"
        choice = SelectKBest(k=NFeatures)
        resultsEUCForNFeatures = []
        for k in [1, 3, 5, 7]:
            print(NFeatures, k)
            knn = CSMKNN(k, meassure=euc, type="min")
            successRates = vectorCrossreferencing(X, y, 5, choice, knn)
            resultsEUCForNFeatures.append(np.mean(successRates))
        resultsEUC.append(resultsEUCForNFeatures)

    # Check success of recognition for all combinations of 
    # number of features and number of nearest neighbours with cosine similarity
    resultsCOS = []
    for NFeatures in range(1, 25):
        if NFeatures == 24:
            NFeatures = "all"
        choice = SelectKBest(k=NFeatures)
        resultsCOSForNFeatures = []
        for k in [1, 3, 5, 7]:
            print(NFeatures, k)
            knn = CSMKNN(k, meassure=csm, type="max")
            successRates = vectorCrossreferencing(X, y, 5, choice, knn)
            resultsCOSForNFeatures.append(np.mean(successRates))
        resultsCOS.append(resultsCOSForNFeatures)

    np.savetxt("resultsEUC.ods", resultsEUC, delimiter=",")
    np.savetxt("resultsCOS.ods", resultsCOS, delimiter=",")

    # Create pandas dataframes and write them to excel
    dfEUC = pandas.DataFrame(resultsEUC)
    writerEUC = pandas.ExcelWriter('resultsEUC.xlsx', engine = 'xlsxwriter')
    dfEUC.to_excel(writerEUC, sheet_name = 'Euclidean-distance')
    worksheetEUC = writerEUC.sheets['Euclidean-distance']
    worksheetEUC.conditional_format('B2:E25', {'type': '3_color_scale'})
    writerEUC.save()

    dfCOS = pandas.DataFrame(resultsCOS)
    writerCOS = pandas.ExcelWriter('resultsCOS.xlsx', engine = 'xlsxwriter')
    dfCOS.to_excel(writerCOS, sheet_name='Cosine-meassure')   
    worksheetCOS = writerCOS.sheets['Cosine-meassure']
    worksheetCOS.conditional_format('B2:E25', {'type': '3_color_scale'})
    writerCOS.save()


if __name__ == "__main__":
    executor = ProcessPoolExecutor(1)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(exercise2_csmknn())