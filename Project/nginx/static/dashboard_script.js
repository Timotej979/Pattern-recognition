// Set chunk size for chunked file transfer
const CHUNK_SIZE = 1024 * 1024; // 1 MB

async function uploadFile() {
    // Get file from input
    chunkFile = document.querySelector('#fileupload').files[0];
    fileName = chunkFile.name;

    // Split file into chunks
    chunks = [];
    for (let i = 0; i < chunkFile.size; i += CHUNK_SIZE) {
        chunks.push(chunkFile.slice(i, i + CHUNK_SIZE));
    }

    // Upload chunks
    var codeCounter = 0;
    for (let j = 0; j < chunks.length; j++) {
        // Create form data
        chunkFormData = new FormData();
        chunkFormData.append('fileName', fileName);
        chunkFormData.append('file', chunks[j]);
        chunkFormData.append('chunkIndex', j);
        chunkFormData.append('totalChunks', chunks.length);
        
        // Send chunk
        await axios.post('/recognition-web/v1/uploadData', chunkFormData).then(function(response) {
            if (response.status >= 200 && response.status < 300) {
                codeCounter = codeCounter + 1;
                
                if ((codeCounter == 1) && (chunks.length > 1)) {
                    alert("Uploading data will take a while, number of chunks to upload: " + chunks.length)
                }

                if (codeCounter == chunks.length) {
                    alert("Data upload  was successful.");
                }
            } else {
                alert("Data upload failed.");
            }
        });
    } 
}

async function bodyOnload(){
    // Get feature set table
    var table = document.getElementById("feature-set-table");

    // Get feature sets from server and add to table
    await axios.get('/recognition-web/v1/getFeatureSets').then(function(response) {
        if (response.status >= 200 && response.status < 300) {
            // Get data from response
            var data = response.data;

            // Remove status code from data
            data = data.message;

            // Get data in form of arrays
            let FeatureSets = data.FeatureSets;
            let NumberOfFeatures = data.NumOfRows;

            // Add data to table
            for (var i = 0; i < FeatureSets.length; i++) {
                var row = table.insertRow(i + 1);
                var cell1 = row.insertCell(0);
                var cell2 = row.insertCell(1);
                cell1.innerHTML = FeatureSets[i];
                cell2.innerHTML = NumberOfFeatures[i];
            }

        } else {
            alert("Failed to get data.");
        }
    });
}
