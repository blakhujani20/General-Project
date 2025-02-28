from flask import Flask, render_template, request, send_file
from sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from collections import Counter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config["SQLALCHEMy_DATABASE_URI"] = "sqlite://text_analysis.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Database
class textanalysis(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    filename = db.Column(db.string(255), nullable=False)
    num_words = db.Column(db.Integer, nullable=False)
    num_chars = db.Column(db.Integer, nullable=False)
    top_words = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TextAnalysis {self.filename}>"

with app.app_context():
    db.create_all()

# Function to analyze text
def analyze_text(text, word_limit):
    words = text.split()
    num_words = len(words)
    num_chars = len(text)
    word_counts = Counter(words).most_common(word_limit)  # Use selected number of frequent words
    return num_words, num_chars, word_counts

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"
        file = request.files["file"]
        if file.filename == "":
            return "No selected file"
        
        if file and file.filename.endswith(".txt"):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)
            
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()

            # Get the word limit from the slider input
            word_limit = int(request.form.get("word_limit", 10))
            
            num_words, num_chars, word_counts = analyze_text(text, word_limit)
            top_words_str = ", ".join([f"{word} ({count})" for word, count in word_counts])


            new_entry = textanalysis(
                filename=file.filename,
                num_words=num_words,
                num_chars=num_chars,
                top_words = top_words_str
            )
            db.session.add(new_entry)
            db.session.commit()


            return render_template("index.html", num_words=num_words, num_chars=num_chars, word_counts=word_counts,file_id=new_entry.id)
        else:
            return "Invalid file type. Please upload a .txt file."

    return render_template("index.html")

@app.route("/download/<int:file_id>")
def download_report(file_id):
    entry = textanalysis.query.get(file_id)

    if not entry:
        return "Report not found", 404

    pdf_filename = f"reports/{entry.filename}_report.pdf"
    os.makedirs("reports", exist_ok=True)

    c = canvas.Canvas(pdf_filename, pagesize = letter)
    c.drawstring(100, 750, f"Analysis Report for {entry.filename}")
    c.drawString(100, 730, f"Total Words: {entry.num_words}")
    c.drawString(100, 710, f"Total Characters: {entry.num_chars}")
    c.drawString(100, 690, f"Top Words: {entry.top_words}")
    c.drawString(100, 670, f"Timestamp: {entry.timestamp}")
    c.save()

    return send_file(pdf_filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
