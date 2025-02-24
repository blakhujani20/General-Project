from flask import Flask, render_template, request
import os
from collections import Counter

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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
            return render_template("index.html", num_words=num_words, num_chars=num_chars, word_counts=word_counts)
        else:
            return "Invalid file type. Please upload a .txt file."

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
