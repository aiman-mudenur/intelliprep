from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>IntelliPrep AI</title>

<style>
body {
 font-family: Arial;
 background: linear-gradient(to right, #0f172a, #1e293b);
 color: white;
 text-align: center;
 padding: 20px;
}

.container {
 max-width: 750px;
 margin: auto;
 background: #1e293b;
 padding: 25px;
 border-radius: 15px;
 box-shadow: 0 0 25px rgba(0,0,0,0.6);
}

textarea {
 width: 90%;
 height: 100px;
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
}

button:hover {
 background: #2563eb;
}

h2 {
 color: #38bdf8;
}

.result {
 margin-top: 10px;
 font-size: 16px;
}

</style>
</head>

<body>

<div class="container">

<h2>🚀 IntelliPrep AI</h2>
<p>AI-powered Interview & Resume Intelligence System</p>

<h3>Interview Evaluation</h3>
<textarea id="ans" placeholder="Type your answer..."></textarea><br>
<button onclick="evalAns()">Evaluate</button>
<p id="res" class="result"></p>

<hr>

<h3>Resume Analyzer</h3>
<textarea id="resume" placeholder="Paste resume text..."></textarea><br>
<button onclick="analyze()">Analyze</button>
<p id="res2" class="result"></p>

</div>
<select id="question">
<option>Tell me about yourself</option>
<option>Describe a challenge</option>
<option>Why should we hire you?</option>
</select>
<script>

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
}

async function analyze(){
 let txt=document.getElementById('resume').value;

 let res=await fetch('/resume',{
  method:'POST',
  headers:{'Content-Type':'application/json'},
  body:JSON.stringify({text:txt})
 });

 let data=await res.json();

 document.getElementById('res2').innerHTML =
 "<b>Detected Skills:</b> "+data.found+"<br><b>Missing Skills:</b> "+data.missing;
}

</script>

</body>
</html>
"""

# -------------------------------
# Interview Evaluation Logic
# -------------------------------
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
        feedback.append("Include more relevant keywords")

    if not feedback:
        feedback.append("Excellent answer")

    return jsonify({
        "score": min(score,10),
        "feedback": ", ".join(feedback)
    })


# -------------------------------
# Resume Analyzer
# -------------------------------
@app.route('/resume', methods=['POST'])
def resume():
    text = request.json.get("text","").lower()

    skills = ["python","sql","react","machine learning","cloud"]

    found = [s for s in skills if s in text]
    missing = [s for s in skills if s not in text]

    feedback = []
    if "project" not in text:
        feedback.append("Add projects section")

    return jsonify({
        "found": found,
        "missing": missing,
        "feedback": feedback
    })


if __name__ == "__main__":
    app.run()
