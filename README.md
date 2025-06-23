# Signing for Care: ASL Learning Tool for Emergency Responders

This repository contains the codebase for **"Signing for Care: A Demo and Initial Evaluation of an American Sign Language Learning Tool for Emergency Medical Responders"**, a prototype designed to support emergency medical service (EMS) providers in acquiring essential ASL vocabulary. 

Deaf and Hard of Hearing (DHH) individuals face serious communication barriers in emergency healthcare settings, where the absence of interpreters can result in delayed or improper treatment. This system provides EMS personnel with:

- A vocabulary learning module tailored to emergency contexts
- AI-based recognition and feedback to practice ASL terms
- Video-based input and testing system for real-time feedback

---

## 📁 Project Structure
```
├── asl-website/              # Frontend files (HTML/JS/UI for sign testing)
    ├─backend.js              # Node.js backend (video upload + Python inference)
├── model/                    # Python scripts and ML models for recognition 
├── .firebase/ and config     # Firebase (optional, not active in this version)
```

---

## 🔧 Installation

### 1. Clone this repository
```bash
git clone https://github.com/chaelin0722/ASL-emergency.git
cd asl-emergency
```

### 2. Install Node.js dependencies (for backend)
```bash
npm install
```

### 3. Set up Python environment (optional, for model)
If using the Python-based inference system:
```bash
cd model
pip install -r requirements.txt
```

---

## ▶️ Running the Program

### 1. Start the Node.js Backend Server
This handles file uploads and calls the Python recognition script.
```bash
node backend.js
```
By default, it runs on `http://localhost:3000`

### 2. Start the Frontend
From the root directory:
```bash
python3 -m http.server 8080
```
Visit the application in your browser at: `http://localhost:8080/asl-website/`

---

## ✨ Features
- Upload a signing video and run inference to identify the signed ASL term
- Receive top predictions and immediate visual feedback
- Interactive testing mode with retry logic:
  - 1st wrong attempt → retry
  - 2nd wrong attempt → skip and proceed to next term
- Vocabulary focused on 79 emergency-related ASL glosses

---

## 👩‍⚕️ Target Users
- EMS personnel (paramedics, EMTs)
- First responders in the field
- Potential future use by primary care physicians and pharmacists

---


If you have any issues running the project, please create an issue or contact the maintainers.
