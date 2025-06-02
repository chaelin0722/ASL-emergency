const express = require("express");
const cors = require("cors");
const multer = require("multer");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

// File storage config
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, "/Users/madhangikrishnan/Documents/GitHub/krishnanmclaren-capstone/asl-website/recorded-videos"); // directory for save files
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
    const extension = path.extname(file.originalname);
    cb(null, `${file.fieldname}-${uniqueSuffix}${extension}`);
  },
});

const app = express(); // creates webapp
app.use(cors());
app.use(express.json());
const upload = multer({ storage: storage }); // initializes upload setup

// end point of processing video 
app.post("/process-video", express.json(), async (req, res) => {
  console.log("request received", req.body);
  console.log("filename received:", req.body.filename);

  const filename = req.body.filename; // passed from frontend

  if (!filename) {
    console.log("no filename provided");
    return res.status(400).json({error: "no filename provided"});
  }

  const videoDir = "/Users/madhangikrishnan/Documents/GitHub/krishnanmclaren-capstone/asl-website/recorded-videos";
  const videoPath = path.join(videoDir, "recorded-video.webm");
/**
  // create JSON file path (save in the same dir) 
  // const path = require("path"); // path module
  const jsonPath = path.join(
  // path.dirname(videoPath), // video file dir
  videoDir,
  `${path.basename(filename, path.extname(filename))}.json`
);
**/

/**
  const pythonProcess = spawn("python3", [
    "/Users/madhangikrishnan/Documents/GitHub/krishnanmclaren-capstone/model/ST-GCN/model.py",
    "--video",
    videoPath,
  ]);

**/

/**
  // Run Python Script
  let pythonProcess;
  if (req.body.scriptName === "Submit") {
      pythonProcess = spawn("python3", [
        "C:\\Users\\calyp\\OneDrive\\Desktop\\GitHub\\krishnanmclaren-capstone\\model\\ST-GCN\\model.py",
        "--video",
        videoPath,
      ]);

  }

**/

//!!
app.post('/recognize', upload.single('video'), (req, res) => {
  const python = spawn('python3', ['model.py', '--video', req.file.path]);

  let resultData = '';
  python.stdout.on('data', (data) => {
    resultData += data.toString();
  });

  python.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  python.on('close', (code) => {
    try {
      const resultJson = JSON.parse(resultData);
      res.json(resultJson); // or wrap in { predictions: resultJson }
    } catch (err) {
      console.error("JSON parse error:", err);
      res.status(500).json({ error: "Failed to parse recognition result" });
    }
  });
});

//!!

console.log("starting python process");

const pythonProcess = spawn("/opt/anaconda3/envs/backend/bin/python", ["/Users/madhangikrishnan/Documents/GitHub/krishnanmclaren-capstone/model/ST-GCN/model.py",
  "--video", videoPath,
]);


pythonProcess.stdout.on("data", (data) => {
  console.log(`python stdout: ${data}`);
});

pythonProcess.stderr.on("data", (data) => {
  console.error(`python stderr: ${data}`);
});

// handle python process exit
pythonProcess.on("close", (code) => {
  if (code !== 0) {
    return res.status(500).json({ error: "Python script failed to process the video." });
  }

  const jsonPath = path.join(videoDir, "recorded-video.json");

  console.log(`Reading JSON result from: ${jsonPath}`);
  fs.readFile(jsonPath, "utf8", (err, data) => {
    if (err) {
      console.error("Error reading JSON file:", err);
      return res.status(500).json({ error: "Failed to read output JSON file." });
    } else {
      console.log("JSON File Data:", data);
    }
    
    res.setHeader("Content-Type", "application/json");
    res.setHeader("Content-Disposition", `attachment; filename=${path.basename(jsonPath)}`);
    res.send(data);
  });

    try {
      res.setHeader("Content-Type", "application/json");
      res.setHeader("Content-Disposition", `attachment; filename=${path.basename(jsonPath)}`);
      res.send(data);
    } catch (e) {
      console.error("failed to send response:", e);
    }
  });
});


// Test root
app.get("/", (req, res) => {
  res.send("Server is running and ready to receive requests!");
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
