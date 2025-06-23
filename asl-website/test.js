//firebase

//import { db } from "./firebase.js";
//import { collection, addDoc } from "firebase/firestore";
// Firebase config
/*const firebaseConfig = {
  apiKey: "AIzaSyCj958ZTc_Vxj6lCcVO_TdIqQ3IcY5sk9o",
  authDomain: "asl-ems.firebaseapp.com",
  projectId: "asl-ems",
  storageBucket: "asl-ems.appspot.com",
  messagingSenderId: "686729704182",
  appId: "1:686729704182:web:0e6c00020412f8a659b2d7"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Initialize Firestore
const db = firebase.firestore();*/


// init
let terms = JSON.parse(localStorage.getItem("terms"));
if (!terms) {
  const allTerms = [{term: "ARM"}, {term: "BACK"}, {term: "EAR"}, {term: "EYES"}, {term: "CHEST"}, {term: "FACE"}, {term: "FINGER"}];
  const retryTermsRaw = JSON.parse(localStorage.getItem("reviewTerms") || "[]");
  const retryTerms = Array.from(new Set(retryTermsRaw.filter(t => typeof t === 'string' && t !== "null")));
  terms = [...allTerms.map(t => t.term), ...retryTerms];
  localStorage.setItem("terms", JSON.stringify(terms)); // init
}
console.log("terms (query):", terms);

// firebase init summary
/*if (!localStorage.getItem("recognitionSummary")) {
  localStorage.setItem("recognitionSummary", JSON.stringify({
    totalAttempts: 0,
    termsTested: [],s
    wrongTermsPushedToReview: []
  }));
}*/


let currentIndex = parseInt(localStorage.getItem("currentIndex") || "0", 10);


function showNextTerm() {
    const wasCorrect = localStorage.getItem("wasCorrect");

    if(wasCorrect === "true"){

        // remove from term list
        terms.splice(currentIndex, 1);
        currentIndex++;
        localStorage.setItem("currentIndex", currentIndex);
    }

    // remove
    localStorage.removeItem("wasCorrect");

    if (currentIndex >= terms.length) {
        document.getElementById("term-display").innerText = "🎉 You've completed all terms!";
        localStorage.removeItem("testedTerm");
        localStorage.removeItem("currentIndex");

        // hide all the buttons
        startBtn.style.display = "none";
        stopBtn.style.display = "none";
        submitBtn.style.display = "none";
        recordedVideo.style.display = "none";

        return;
    }

    const selectedTerm = terms[currentIndex];
    document.getElementById("term-display").innerText = selectedTerm;
    localStorage.setItem("testedTerm", selectedTerm);


}


const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const submitBtn = document.getElementById('submit-btn');
console.log("submit button element:", submitBtn);
const recordedVideo = document.getElementById('recordedVideo');

let mediaRecorder;
let recordedChunks = [];
let stream;

console.log("test.js is loaded");

document.addEventListener('DOMContentLoaded', () => {
    let terms = JSON.parse(localStorage.getItem("terms") || "null");

    const testedTerm = localStorage.getItem('testedTerm');

    console.log("check term list:", terms);
    if (testedTerm) {
        const idx = terms.indexOf(testedTerm);
        if (idx !== -1) {
            currentIndex = idx;
            localStorage.setItem("currentIndex", currentIndex);
        }
    }

    showNextTerm();
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


            const tracks = stream.getTracks();
            tracks.forEach(track => track.stop());
            recordedVideo.srcObject = null;

            // transfer Blob as FormData to server
            const formData = new FormData();
            formData.append("video", blob, "recorded-video.webm");

            try {
                const response = await fetch("http://localhost:3000/upload-video", {
                    method: "POST",
                    body: formData,
                });

                const result = await response.json();
                console.log("Recognition result:", result);
                localStorage.setItem("recognitionResult", JSON.stringify(result));

            } catch (error) {
                console.error("Failed to upload video:", error);
            }

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

        //firebase json
/*
             // 🎯 여기서 새로운 로그 json 만들어!
        const testedTerm = localStorage.getItem("testedTerm");
        const wasCorrect = localStorage.getItem("wasCorrect") === "true";

        const retryCountKey = `retryCount_${testedTerm}`;
        const retryCount = parseInt(localStorage.getItem("retryCountKey") || "0", 10);

        const userLog = {
            timestamp: new Date().toISOString(),
            userId: "user_1", //
            testedTerm: testedTerm,
            wasCorrect: wasCorrect,
            retryCount: retryCount,
        };

        console.log("Uploading to Firebase:", userLog);

        // Firebase에 업로드
        //await addDoc(collection(db, "user_logs"), userLog);
        await db.collection("user_logs").add(userLog);*/

        // Redirect to feedback page after saving result
        window.location.replace("./feedback.html");

    } catch (error) {
        console.log(`Request failed: ${error.message}`);
    }
});