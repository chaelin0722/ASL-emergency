require("dotenv").config();
const admin = require("firebase-admin");

const fs = require("fs");

// initialize firebase admin SDK
const serviceAccount = JSON.parse(process.env.FIREBASE_CREDENTIALS.replace(/\\n/g, '\n'));

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

const db = admin.firestore();

// load JSON file
const data = JSON.parse(fs.readFileSync("video-metadata.json", "utf-8"));

// import data into firestore
(async () => {
  const collectionName = "term-videos";
  const batch = db.batch();

  for (const [docId, docData] of Object.entries(data)) {
    const docRef = db.collection(collectionName).doc(docId);
    batch.set(docRef, docData);
  }

  await batch.commit();
  console.log("Data imported successfully!");
})();