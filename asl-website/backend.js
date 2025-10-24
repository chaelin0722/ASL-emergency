const express = require("express");
const cors = require("cors");
const multer = require("multer");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const app = express();
app.use(cors());
app.use(express.json());

// File storage config
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, "ASL-emergency-final/ASL-emergency/asl-website/recorded-videos");
  },
  filename: function (req, file, cb) {
    cb(null, "recorded-video.webm");  // Always overwrite with same name
  },
});
const upload = multer({ storage: storage });

// upload video
app.post("/upload-video", upload.single("video"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "No video uploaded." });
  }

});

// when hit submit button, process python recognition code.
app.post("/process-video", (req, res) => {
  console.log("request received", req.body);
  console.log("filename received:", req.body.filename);

  // define values
  const videoDir = "ASL-emergency-final/ASL-emergency/asl-website/recorded-videos";
  const videoPath = path.join(videoDir, req.body.filename);
  // JSON file should have same name as video but with .json extension
  const jsonFilename = req.body.filename.replace(/\.[^/.]+$/, ".json");
  const jsonPath = path.join(videoDir, jsonFilename);

  // run python code
  const python = spawn("python3", [
    "ST-GCN/model.py",
    "--video",
    videoPath,
  ], {
    cwd: "ASL-emergency-final/ASL-emergency/model"  // Set working directory to model folder
  });

  // make json
  let resultData = "";

  python.stdout.on("data", (data) => {
    resultData += data.toString();
    //// check
    console.log("#####Python STDOUT:", data.toString());
  });

  python.stderr.on("data", (data) => {
    console.error(`stderr: ${data}`);
  });

  python.on("close", (code) => {
    fs.readFile(jsonPath, "utf8", (err, fileData) => {
      if (err) {
        console.error("Error reading JSON file:", err);
        return res.status(500).json({ error: "Failed to read output JSON file." });
      }

      try {
        const resultJson = JSON.parse(fileData);
        res.json(resultJson);
      } catch (parseErr) {
        console.error("Error parsing JSON from file:", parseErr);
        res.status(500).json({ error: "Invalid JSON format in result file." });
      }
    });

  });
});





// route for test
app.get("/", (req, res) => {
  res.send("Server is running and ready to receive requests!");
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
