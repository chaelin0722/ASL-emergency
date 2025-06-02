import { getFirestore, setDoc, doc } from "firebase/firestore";
import { app } from "./firebase-config";

const db = getFirestore(app);

export function saveUserProgress(userId, videoTerm, hasWatched) {
    return setDoc(doc(db, "users", userId, "progress", videoTerm), {
        watched: hasWatched,
        timestamp: Date.now(),
    });
}
