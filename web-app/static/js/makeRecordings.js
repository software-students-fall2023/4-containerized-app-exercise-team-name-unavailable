document.getElementById('startRecording').addEventListener('click', function() {
    //to start recording
    console.log('Recording started');
    this.disabled = true;
    document.getElementById('stopRecording').disabled = false;
});

document.getElementById('stopRecording').addEventListener('click', function() {
    //to stop recording
    console.log('Recording stopped');
    this.disabled = true;
    document.getElementById('startRecording').disabled = false;
});

document.getElementById('recordingForm').addEventListener('submit', function(e) {
    e.preventDefault();
    //to upload recording
    console.log('Recording uploaded');
});
