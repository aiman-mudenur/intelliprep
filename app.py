from flask import Flask, request, jsonify, session, render_template_string
from flask_cors import CORS
import io
import PyPDF2

app = Flask(__name__)
app.secret_key = "intelliprep_secret"
CORS(app)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>IntelliPrep AI</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body {
 font-family: 'Segoe UI', sans-serif;
 background: linear-gradient(to right, #0f172a, #1e293b);
 color: white;
 text-align: center;
 padding: 20px;
}

.container {
 max-width: 800px;
 margin: auto;
 background: #1e293b;
 padding: 25px;
 border-radius: 15px;
 box-shadow: 0 0 25px rgba(0,0,0,0.6);
}

textarea {
 width: 95%;
 height: 110px;
 border-radius: 10px;
 padding: 10px;
 margin: 10px;
 border: none;
 outline: none;
}

button {
 background: #3b82f6;
 color: white;
 padding: 10px 20px;
 border: none;
 border-radius: 8px;
 cursor: pointer;
 margin: 5px;
}

button:hover {
 background: #2563eb;
}

h2 { color: #38bdf8; }

.result {
 margin-top: 10px;
 font-size: 16px;
}

hr { margin: 20px 0; }

input[type=file]{
 margin: 10px;
}

</style>
</head>

<body>

<div class="container">

<h2>🚀 IntelliPrep AI</h2>
<p>AI-powered Interview & Resume Intelligence System</p>

<!-- Question Dropdown -->
<select id="question">
<option>Why should we hire you?</option>
<option>Describe a challenge you faced</option>
<option>Tell me about yourself</option>
</select>

<h3>Interview Evaluation</h3>
<textarea id="ans" placeholder="Type or speak your answer..."></textarea><br>

<button onclick="startVoice()">🎤 Speak</button>
<button onclick="evalAns()">Evaluate</button>

<p id="res" class="result"></p>

<!-- Graph -->
<canvas id="chart" height="120"></canvas>

<hr>

<h3>Resume Analyzer</h3>

<textarea id="resume" placeholder="Paste resume text..."></textarea><br>
<button onclick="analyzeText()">Analyze Text</button>

<br><br>

<input type="file" id="pdfFile">
<button onclick="uploadPDF()">Upload PDF</button>

<p id="res2" class="result"></p>

</div>

<script>

// ------------------ Voice Input ------------------
function startVoice(){
 const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
 recognition.start();
 recognition.onresult = function(event){
   document.getElementById("ans").value = event.results[0][0].transcript;
 }
}

// ------------------ Chart ------------------
let scores = [];
let chart;

function updateChart(newScore){
 scores.push(newScore);

 if(chart) chart.destroy();

 const ctx = document.getElementById('chart');
 chart = new Chart(ctx, {
   type: 'line',
   data: {
     labels: scores.map((_,i)=>"Attempt "+(i+1)),
     datasets: [{
       label: 'Score Progress',
       data: scores
     }]
   }
 });
}

// ------------------ Evaluation ------------------
async function evalAns(){
 let ans=document.getElementById('ans').value;

 let res=await fetch('/eval',{
  method:'POST',
  headers:{'Content-Type':'application/json'},
  body:JSON.stringify({answer:ans})
 });

 let data=await res.json();

 document.getElementById('res').innerHTML =
 "<b>Score:</b> "+data.score+"/10 <br><b>Feedback:</b> "+data.feedback;

 updateChart(data.score);
}

// ------------------ Resume TEXT ------------------
async function analyzeText(){
 let txt=document.getElementById('resume').value;

 let res=await fetch('/resume_text',{
  method:'POST',
  headers:{'Content-Type':'application/json'},
  body:JSON.stringify({text:txt})
 });

 let data=await res.json();

 document.getElementById('res2').innerHTML =
 "<b>Detected:</b> "+data.found+"<br><b>Missing:</b> "+data.missing;
}

// ------------------ Resume PDF ------------------
async function uploadPDF(){
 let file=document.getElementById('pdfFile').files[0];
 let formData=new FormData();
 formData.append("file",file);

 let res=await fetch('/resume_pdf',{
  method:'POST',
  body:formData
 });

 let data=await res.json();

 document.getElementById('res2').innerHTML =
 "<b>Detected:</b> "+data.found+"<br><b>Missing:</b> "+data.missing;
}

</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

# ------------------ Evaluation Logic ------------------
@app.route('/eval', methods=['POST'])
def eval():
    ans = request.json.get("answer","").lower()
    score = 0
    feedback = []

    keywords = ["team","project","challenge","solution"]
    matches = sum(1 for k in keywords if k in ans)
    score += matches * 2

    if len(ans) > 80:
        score += 2
    else:
        feedback.append("Answer too short")

    if "example" in ans or "because" in ans:
        score += 2
    else:
        feedback.append("Add examples")

    if matches < 2:
        feedback.append("Include more keywords")

    if not feedback:
        feedback.append("Excellent answer")

    return jsonify({
        "score": min(score,10),
        "feedback": ", ".join(feedback)
    })

# ------------------ Resume TEXT ------------------
@app.route('/resume_text', methods=['POST'])
def resume_text():
    text = request.json.get("text","").lower()

    skills = ["python","sql","react","machine learning","cloud"]
    found = [s for s in skills if s in text]
    missing = [s for s in skills if s not in text]

    return jsonify({"found": found, "missing": missing})

# ------------------ Resume PDF ------------------
@app.route('/resume_pdf', methods=['POST'])
def resume_pdf():
    file = request.files['file']
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))

    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text().lower()

    skills = ["python","sql","react","machine learning","cloud"]
    found = [s for s in skills if s in text]
    missing = [s for s in skills if s not in text]

    return jsonify({"found": found, "missing": missing})


if __name__ == "__main__":
    app.run()
