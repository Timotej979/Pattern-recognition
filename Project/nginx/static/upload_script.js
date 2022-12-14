// Set chunk size for chunked file transfer
const CHUNK_SIZE = 1024 * 1024; // 1 MB

async function uploadFile() {
    const chunkFile = document.querySelector('#fileupload').files[0];

    const chunks = [];
    for (let i = 0; i < chunkFile.size; i += CHUNK_SIZE) {
        chunks.push(chunkFile.slice(i, i + CHUNK_SIZE));
    }

    var codeCounter = 0;
    for (let j = 0; j < chunks.length; j++) {
        const chunkFormData = new FormData();
        chunkFormData.append('file', chunks[j]);
        chunkFormData.append('chunkIndex', j);
        chunkFormData.append('totalChunks', chunks.length);
        await axios.post('/recognition-web/v1/uploadData', chunkFormData).then(function(response) {
            if (response.status >= 200 && response.status < 300) {
                codeCounter = codeCounter + 1;
            } 
        });
    } 

    if (codeCounter == chunks.length){
        alert("Data upload was successful.");
    } else {
        alert("Data upload failed.");
    }

}
