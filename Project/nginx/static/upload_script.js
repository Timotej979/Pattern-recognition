// Set chunk size for chunked file transfer
const CHUNK_SIZE = 1024 * 1024; // 1 MB

async function uploadFile() {
    chunkFile = document.querySelector('#fileupload').files[0];
    fileName = chunkFile.name;

    chunks = [];
    for (let i = 0; i < chunkFile.size; i += CHUNK_SIZE) {
        chunks.push(chunkFile.slice(i, i + CHUNK_SIZE));
    }

    var codeCounter = 0;
    for (let j = 0; j < chunks.length; j++) {
        chunkFormData = new FormData();
        chunkFormData.append('fileName', fileName);
        chunkFormData.append('file', chunks[j]);
        chunkFormData.append('chunkIndex', j);
        chunkFormData.append('totalChunks', chunks.length);
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
