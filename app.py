from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h2>Interview Evaluation</h2>
    <textarea id='ans'></textarea><br>
    <button onclick='evalAns()'>Evaluate</button>
    <p id='res'></p>

    <hr>

    <h2>Resume Analyzer (Paste Text)</h2>
    <textarea id='resume'></textarea><br>
    <button onclick='analyze()'>Analyze</button>
    <p id='res2'></p>

<script>
async function evalAns(){
 let ans=document.getElementById('ans').value;
 let res=await fetch('/eval',{
  method:'POST',
  headers:{'Content-Type':'application/json'},
  body:JSON.stringify({answer:ans})
 });
 let data=await res.json();
 document.getElementById('res').innerText="Score:"+data.score+" "+data.feedback;
}

async function analyze(){
 let txt=document.getElementById('resume').value;
 let res=await fetch('/resume',{
  method:'POST',
  headers:{'Content-Type':'application/json'},
  body:JSON.stringify({text:txt})
 });
 let data=await res.json();
 document.getElementById('res2').innerText="Missing:"+data.missing;
}
</script>
    """

@app.route('/eval', methods=['POST'])
def eval():
    ans = request.json.get("answer","").lower()
    score = 0

    if "team" in ans: score+=2
    if len(ans)>50: score+=2
    if "example" in ans: score+=2

    return jsonify({"score":score,"feedback":"Improve with examples"})

@app.route('/resume', methods=['POST'])
def resume():
    text = request.json.get("text","").lower()

    skills=["python","sql","react"]
    missing=[s for s in skills if s not in text]

    return jsonify({"missing":missing})

if __name__ == "__main__":
    app.run()