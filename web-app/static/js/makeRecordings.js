let recorder;
let audioChunks = [];

document.getElementById('startRecording').addEventListener('click', function() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
            recorder = new Recorder({
                encoderPath: "encoderWorker.min.js",
                stream: stream
            });

            recorder.start().then(() => {
                console.log('Recording started');
                document.getElementById('startRecording').disabled = true;
                document.getElementById('stopRecording').disabled = false;
            });
        })
        .catch(function(err) {
            console.error('Error accessing audio stream:', err);
        });
});

document.getElementById('stopRecording').addEventListener('click', function() {
    recorder.stop().then(({blob}) => {
        window.audioBlob = blob;
        console.log('Recording stopped');
        document.getElementById('audioPlayback').src = URL.createObjectURL(blob);
        document.getElementById('audioPlayback').style.display = 'block';
        document.getElementById('stopRecording').disabled = true;
        document.getElementById('startRecording').disabled = false;
    });
});

document.getElementById('recordingForm').addEventListener('submit', function(e) {
    e.preventDefault();

    if (!window.audioBlob) {
        alert("No recording available. Please record something first.");
        return;
    }

    let formData = new FormData();
    formData.append('audio', window.audioBlob, 'audio.opus');
    formData.append('username', document.getElementById('username').value);
    formData.append('name', document.getElementById('name').value);

    fetch('/upload', {
      method: 'POST',
      body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
      console.log('Success:', data);
      alert("Recording uploaded successfully.");
    })
    .catch((error) => {
      console.error('Error:', error);
      alert("Failed to upload recording.");
    });
});
