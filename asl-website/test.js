const terms = [{term: "ITCH"}, {term: "EARS"}, {term: "NOSE"}, {term: "BLOOD"}];

const termBtn = document.getElementById('term-btn');
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const submitBtn = document.getElementById('submit-btn');
console.log("submit button element:", submitBtn);
const recordedVideo = document.getElementById('recordedVideo');

let mediaRecorder;
let recordedChunks = [];
let stream;

console.log("test.js is loaded");

termBtn.addEventListener('click', () => {
    const randomIndex = Math.floor(Math.random() * terms.length); // randomizes list of terms in module
    const selectedTerm = terms[randomIndex].term; // generates term from list
    document.getElementById("term-display").innerText = selectedTerm;
    localStorage.setItem('testedTerm', selectedTerm);  
});

document.addEventListener('DOMContentLoaded', () => {
    const pageUrl = window.location.href;
    const moduleTitle = pageUrl.substring(pageUrl.lastIndexOf('/') + 1, pageUrl.lastIndexOf('.html')).replace(/-/g, ' ');
    console.log(moduleTitle);

    const buttonItems = JSON.parse(localStorage.getItem('buttonItems')) || [];
    const moduleIndex = buttonItems.findIndex(item => item.title.toLowerCase().replace(/[^a-z0-9]+/g, '-') + '.html' === pageUrl.substring(pageUrl.lastIndexOf('/') + 1));

    if (moduleIndex !== -1) {
        localStorage.setItem(`tested-${moduleIndex}`, 'tested');
    }

    const testedTerm = localStorage.getItem('testedTerm');
    if (testedTerm) {
        const termIndex = terms.findIndex(termObj => termObj.term === testedTerm);
        if (termIndex !== -1) {
            terms.splice(termIndex, 1);
        }
        localStorage.removeItem('testedTerm');
    }
});

startBtn.addEventListener('click', async () => {
    console.log("Start button clicked!");

    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        recordedVideo.srcObject = stream;
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = event => {
            console.log("Video recorded!");
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {
            const blob = new Blob(recordedChunks, { type: 'video/webm' });
            recordedVideo.src = URL.createObjectURL(blob);
            recordedVideo.controls = true;
            recordedChunks = [];

            const reader = new FileReader();
            reader.onload = function() {
                localStorage.setItem('recordedVideoData', reader.result);
            };
            reader.readAsDataURL(blob);

            try {
                const handle = await window.showSaveFilePicker({
                    suggestedName: 'recorded-video.webm',
                    types: [{
                        description: 'WebM video',
                        accept: { 'video/webm': ['.mp4'] },
                    }],
                });
                const writable = await handle.createWritable();
                await writable.write(blob);
                await writable.close();

                console.log('Video saved successfully!');
            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.error('Error saving video:', error);
                }
            }

            const tracks = stream.getTracks();
            tracks.forEach(track => track.stop());
            recordedVideo.srcObject = null;
        };

        mediaRecorder.onerror = (error) => {
            console.error("MediaRecorder error:", error);
        };

        mediaRecorder.start();
        console.log("MediaRecorder started. State:", mediaRecorder.state);
        startBtn.disabled = true;
        stopBtn.disabled = false;

    } catch (error) {
        console.error("Error accessing media devices:", error);
    }
});

stopBtn.addEventListener('click', () => {
    console.log("Stop button clicked!");
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
});

stopBtn.disabled = true;

submitBtn.addEventListener('click', async () => {
    console.log("submitted!");
    const filename = "recorded-video.webm";
    console.log("sending filename to server:", filename);
  
    try {
        const response = await fetch("http://localhost:3000/process-video", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename: filename }),
        });

        console.log("response received");

        if (!response.ok) {
            console.log(`Error: ${response.statusText}`);
            return;
        }

        // Parse JSON result instead of downloading it
        const resultJson = await response.json();
        console.log("Parsed JSON result:", resultJson);

        // Save it to localStorage for feedback.html to read
        localStorage.setItem("recognitionResult", JSON.stringify(resultJson));

        // Redirect to feedback page after saving result
        window.location.replace("./feedback.html");

    } catch (error) {
        console.log(`Request failed: ${error.message}`);
    }
});