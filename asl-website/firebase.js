// Import the functions you need from the SDKs you need
// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCj958ZTc_Vxj6lCcVO_TdIqQ3IcY5sk9o",
  authDomain: "asl-ems.firebaseapp.com",
  projectId: "asl-ems",
  storageBucket: "asl-ems.firebasestorage.app",
  messagingSenderId: "686729704182",
  appId: "1:686729704182:web:0e6c00020412f8a659b2d7"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Export to window
const db = firebase.firestore();