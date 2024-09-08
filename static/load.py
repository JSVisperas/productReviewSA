from flask import Flask, request, jsonify
import torch
from transformers import AutoTokenizer
import pandas as pd
import torch.nn as nn
from transformers import XLMRobertaModel
import numpy as np

app = Flask(__name__)


class CustomXLMRobertaModel(nn.Module):
    def __init__(self, num_labels):
        super(CustomXLMRobertaModel, self).__init__()
        model_name = 'symanto/xlm-roberta-base-snli-mnli-anli-xnli'
        self.roberta = XLMRobertaModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Sequential(
            nn.Linear(768, 512),
            nn.LayerNorm(512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, num_labels)
        )
        self.loss = nn.CrossEntropyLoss()
        self.num_labels = num_labels

    def forward(self, input_ids, attention_mask, labels=None):
        output = self.roberta(input_ids=input_ids,
                              attention_mask=attention_mask)
        output = self.dropout(output.pooler_output)
        logits = self.classifier(output)

        if labels is not None:
            loss = self.loss(logits.view(-1, self.num_labels), labels.view(-1))
            return {"loss": loss, "logits": logits}
        else:
            return logits


# Define the number of labels for classification
num_labels = 2
# Re-instantiate the custom model
model = CustomXLMRobertaModel(num_labels=num_labels)

# Load the model weights and tokenizer
model.load_state_dict(torch.load(
    'custom_xlm_roberta_model.pth',  map_location=torch.device('cpu')))
model.eval()
tokenizer = AutoTokenizer.from_pretrained("./model")


# FOR SINGLE INPUT SENTIMENT ANALYSIS (GET REQUEST)
def analyze_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs
    probabilities = torch.softmax(logits, dim=-1)
    predicted_class = torch.argmax(probabilities, dim=-1).item()
    return predicted_class


# Initialize sets for faster keyword lookups
funclist = {
    'functioning', 'operating', 'works', 'active', 'in use', 'impactful', 'successful',
    'useful', 'practical', 'serviceable', 'performs', 'executes', 'carries out',
    'accomplishes', 'running', 'working', 'handy', 'dependable', 'trustworthy', 'consistent',
    'steady', 'stable', 'streamlined', 'productive', 'competent', 'resourceful',
    'meets expectations', 'functions properly', 'in order', 'beeping', 'sounding', 'alarming',
    'ringing', 'buzzing', 'charges', 'powers', 'energizes', 'replenishes', 'fills', 'connects',
    'links', 'joins', 'interfaces', 'attaches', 'smashes', 'breaks', 'shatters', 'crushes',
    'demolishes', 'malfunction', 'breakdown', 'failure', 'defect', 'glitch', 'arrives', 'reaches',
    'comes', 'shows up', 'lands', 'sends', 'transports', 'provides', 'brings', 'fits', 'suits',
    'matches', 'aligns', 'adapts', 'gumagana', 'sira', 'cuts', 'slices', 'trims', 'shears',
    'chops', 'nakaayos', 'organized', 'arranged', 'sorted', 'heats', 'warms', 'boils', 'cooks',
    'toasts', 'hindi gumagana', 'not working', 'non-functional', 'broken', 'lasted', 'endured',
    'survived', 'remained', 'glitches', 'bugs', 'errors', 'issues', 'faults', 'uses', 'utilizes',
    'employs', 'applies', 'leverages', 'nakakapaso', 'burns', 'overheats', 'scalds', 'correct',
    'creates', 'produces', 'generates', 'forms', 'supports', 'aids', 'assists', 'backs',
    'reinforces', 'leaking', 'dripping', 'seeping', 'oozing', 'drains', 'empties', 'depletes',
    'siphons', 'handles', 'manages', 'grips', 'maneuvering', 'navigating', 'steering', 'guiding',
    'safe', 'secure', 'protected', 'easy', 'simple', 'straightforward', 'effortless', 'install',
    'set up', 'mount', 'place', 'configure', 'expands', 'enlarges', 'extends', 'grows',
    'fitting', 'suitable', 'appropriate', 'matching', 'performing', 'maliit', 'naka-bubble wrap',
    'bubble-wrapped', 'padded', 'protected', 'tamang-tama', 'just right', 'well-suited', 'magaan',
    'lightweight', 'not heavy', 'nag-aano', 'acting up', 'misbehaving', 'bura', 'erased',
    'wiped', 'removed', 'ka-tanggap', 'acceptable', 'hindi magagamit', 'unusable', 'alarm', 'alert',
    'warning', 'siren', 'expiration', 'end date', 'expiry', 'termination', 'frustrating', 'irritating',
    'annoying', 'exasperating', 'replacement', 'substitute', 'new part', 'alternative', 'ripped',
    'torn', 'shredded', 'expire', 'run out', 'end', 'lapse', 'deal', 'bargain', 'offer', 'agreement',
    'installed', 'mounted', 'peephole', 'viewer', 'window', 'observation hole', 'fix', 'repair',
    'mend', 'function', 'purpose', 'role', 'operation', 'leak', 'escape', 'seep', 'breach',
    'charging', 'powering', 'replenishing', 'energizing', 'operate', 'control', 'manage', 'run',
    'non-filled', 'empty', 'unfilled', 'hollow', 'good', 'fine', 'replace', 'substitute', 'exchange',
    'swap', 'fail', 'collapse', 'break down', 'restore', 'firmly', 'properly adjusted', 'correctly set',
    'well-tuned', 'suits needs', 'meets requirements', 'fulfills needs', 'battery life', 'power duration',
    'charge lifespan', 'effective', 'functional', 'operational', 'usable', 'efficient', 'works as expected',
    'functioning', 'beeping', 'charges', 'connects', 'smashes', 'malfunction', 'arrives', 'delivers',
    'operates', 'fits', 'gumagana', 'sira', 'cuts', 'nakaayos', 'heats', 'hindi gumagana', 'lasted',
    'glitches', 'uses', 'nakakapaso', 'accurate', 'makes', 'supports', 'leaking', 'drains', 'handles',
    'maneuvering', 'safe', 'easy', 'install', 'expands', 'fitting', 'not working', 'performing', 'maliit',
    'naka-bubble wrap', 'tamang-tama', 'magaan', 'nag-aano', 'bura', 'ka-tanggap', 'hindi magagamit',
    'alarm', 'expiration', 'frustrating', 'replacement', 'ripped', 'expire', 'deal', 'installed',
    'peephole', 'fixes', 'functionality', 'leakage', 'charging process', 'operates smoothly',
    'replaceable', 'exchangeable', 'substitutable', 'fails', 'repairable', 'fixable', 'mendable',
    'securely', 'suits needs', 'battery life', 'defective unit', 'handle with care'
}

quallist = {
    "quality", "premium", "top-tier", "luxury", "upscale", "balanced expense",
    "high-quality", "superior", "top-notch", "well-made", "expertly crafted", "well-built",
    "solid", "sturdy", "strong", "tough", "reliable", "dependable", "trustworthy", "consistent",
    "secure", "elegant", "refined", "stylish", "graceful", "excellent", "superb", "outstanding",
    "first-rate", "clear", "distinct", "cleanly", "neatly", "smoothly", "nice", "pleasant",
    "agreeable", "even", "sleek", "polished", "comfortable", "cozy", "impressive", "remarkable",
    "flawless", "perfect", "impeccable", "faultless", "great", "adequate", "beautiful", "lovely",
    "charming", "endearing", "inviting", "captivating", "intriguing", "engaging", "compelling",
    "classy", "sophisticated", "timely", "practical", "relevant", "accurate", "detailed",
    "up-to-date", "new", "recent", "fresh", "genuine", "authentic", "original", "true", "unique",
    "classic", "ageless", "high-grade", "top-quality", "finest", "best", "ultimate", "complete",
    "full", "entire", "finished", "accomplished", "well-maintained", "well-protected", "artisanal",
    "handcrafted", "handmade", "design", "plan", "style", "layout", "interesting", "pleasant",
    "delightful", "stunning", "striking", "credible", "sharp", "perceptive", "acute", "tapered",
    "delicate", "fragile", "brittle", "weak", "flimsy", "low-quality", "poor", "subpar", "inadequate",
    "insufficient", "deficient", "damaged", "broken", "faulty", "flawed", "ruined", "shattered",
    "unfit", "unsuitable", "inappropriate", "shoddy", "substandard", "inexpensive resources",
    "cheap materials", "low-cost materials", "material", "material feels cheap", "durable", "matibay"
}

pricelist = {
    "affordable", "economical", "reasonable", "budget-friendly", "cost-effective",
    "value for money", "inexpensive", "expensive", "costly", "high-priced",
    "overpriced", "pricey", "exorbitant", "lavish", "upscale", "extravagant",
    "steep", "excessively high", "high-end", "deals and discounts", "bargain",
    "deal", "steal", "offer", "discounted", "reduced", "marked down", "on sale",
    "fair", "moderate", "pricing and cost", "price", "cost", "rate", "value",
    "fee", "charge", "price point", "cost level", "pricing", "balanced expense",
    "justifiable cost", "worth", "worthwhile", "justifiable", "top-tier",
    "efficiency", "efficient", "good deal", "abot-kaya", "matipid", "makatarungan",
    "maganda ang halaga", "mura", "mahal", "magastos", "mataas ang presyo",
    "sobra sa presyo", "mataas na presyo", "masyadong mahal", "maluhong", "magarbo",
    "matindi ang presyo", "kasunduan", "abot-kayang presyo", "alok", "may diskwento",
    "nabawasan", "binawasan ang presyo", "nasa sale", "katamtaman", "presyo",
    "gastos", "halaga", "bayad", "singil", "presyo ng produkto", "antas ng gastos",
    "pagpepresyo", "sulit",
}

keywords = {
    'functionality': funclist,
    'quality': quallist,
    'price': pricelist
}


# FOR CLASSIFICATION OF REVIEWS
def classify_review(review):
    scores = {'functionality': 0, 'quality': 0, 'price': 0}

    # Tokenize the review
    words = review.lower().split()

    # Score the review based on keyword presence
    for word in words:
        for category, keywords_set in keywords.items():
            if word in keywords_set:
                scores[category] += 1

    # Determine the category with the highest score
    max_category = max(scores, key=scores.get)

    # If all scores are zero, assign "others"
    if all(score == 0 for score in scores.values()):
        return 'others'

    return max_category


@app.route('/analyze', methods=['GET'])
def analyze():
    text = request.args.get('text')  # Get parameter from the URL query string
    if text is None:
        return jsonify({'error': 'No text provided'}), 400

    result = analyze_sentiment(text)
    return jsonify({'sentiment': result})


# FOR CSV FILE PROCESSING (POST REQUEST)
@app.route('/process_csv', methods=['POST'])
def process_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        # Read the CSV file into a pandas DataFrame
        dataDF = pd.read_csv(file, encoding="Latin-1")

        # Define batch size
        batch_size = 32  # Adjust based on available memory
        input_texts = dataDF['text'].tolist()

        # Process in batches
        all_predicted_labels = []
        for i in range(0, len(input_texts), batch_size):
            batch_texts = input_texts[i:i+batch_size]

            # Tokenize the input texts (this will handle multiple texts as a batch)
            inputs = tokenizer(batch_texts, return_tensors="pt",
                               truncation=True, padding=True)

            # Extract input_ids and attention_mask from the tokenized input
            input_ids = inputs["input_ids"]
            attention_mask = inputs["attention_mask"]

            # Disable gradient calculations for inference
            with torch.no_grad():
                # Remove token_type_ids from inputs if it exists
                if "token_type_ids" in inputs:
                    del inputs["token_type_ids"]

                outputs = model(**inputs)
                logits = outputs

                # Compute probabilities
                probabilities = torch.softmax(logits, dim=-1)

                # Get the predicted classes
                predicted_classes = torch.argmax(probabilities, dim=-1)

            # Define the label mapping
            label_mapping = {0: 'Negative', 1: 'Positive'}

            # Map numeric predictions to string labels
            predicted_labels = [label_mapping[class_index]
                                for class_index in predicted_classes.cpu().numpy()]
            all_predicted_labels.extend(predicted_labels)

        # Add predicted labels to the DataFrame
        dataDF['sentiment'] = all_predicted_labels
        # Add categories to each review
        dataDF['category'] = dataDF['text'].apply(classify_review)

        # Convert the DataFrame to JSON
        result_json = dataDF.to_json(orient='records')

        return jsonify(result_json)

    else:
        return jsonify({"error": "Invalid file format, only CSV files are allowed"}), 400


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
