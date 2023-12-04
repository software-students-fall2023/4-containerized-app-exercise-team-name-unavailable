let recorder;
let audioChunks = [];

document.getElementById('startRecording').addEventListener('click', function() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
            recorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });

            recorder.start();

            recorder.addEventListener('dataavailable', function(e) {
                audioChunks.push(e.data);
            });

            console.log('Recording started');
            document.getElementById('startRecording').disabled = true;
            document.getElementById('stopRecording').disabled = false;
        })
        .catch(function(err) {
            console.error('Error accessing audio stream:', err);
        });
});

document.getElementById('stopRecording').addEventListener('click', function() {
    recorder.stop();

    recorder.addEventListener('stop', function() {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm;codecs=opus' });
        window.audioBlob = audioBlob;
        audioChunks = [];

        console.log('Recording stopped');
        document.getElementById('audioPlayback').src = URL.createObjectURL(audioBlob);
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
    formData.append('audio', window.audioBlob, 'audio.webm');
    formData.append('username', document.getElementById('username').value);
    formData.append('name', document.getElementById('recordingName').value);

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
