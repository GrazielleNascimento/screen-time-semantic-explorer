# Capstone Data Science

## Semantic Search over Scientific Articles

## What is this project?

An end-to-end pipeline that turns scientific articles (PDF) into a **semantic search** system. Documents are loaded and split into chunks, each chunk is converted into an embedding (a numeric representation of its meaning), everything is indexed in a vector database, and you can then search by **meaning**, not by exact keywords.

**Example:** searching for "effects of screen time on children" also finds passages about "impact of digital media on minors", even when they do not share the same words.

## Chosen domain

**Effects of screen use on children and adolescents**

Topics covered by the articles:

- Screen time and mental health
- Digital media and childhood obesity
- Impact on sleep and sleep quality
- Cognitive development and learning
- Behavior and socialization
- Interventions and clinical recommendations

**Data source:** 30 open-access scientific articles from **PubMed Central (PMC)**, collected in 2026. PDF file names are their PMC identifiers (e.g. `PMC13589963.pdf`).

## Pipeline (data flow)

```
PDFs (data/raw/)
    |
    v
[loader.py]   Text extraction + chunking
    |
    v
chunks.jsonl (data/processed/)   ~6,000 text chunks
    |
    v
[clean.py]    Removes empty, too-short or invalid chunks
    |
    v
chunks.jsonl (cleaned)
    |
    v
[embedder.py] Embeddings (all-MiniLM-L6-v2) + ChromaDB indexing
    |
    v
ChromaDB (data/chroma/)   Persistent vector database
    |
    v
[search.py]   Semantic search
    |
    v
Results with similarity distance
```

Each step reads the output of the previous one, so every script can be re-run independently.

## Project structure

```
CAPSTONE/
├── data/
│   ├── raw/                 # Original PDFs (30 articles)
│   ├── processed/
│   │   └── chunks.jsonl     # Extracted and cleaned text chunks
│   └── chroma/              # ChromaDB vector database (persisted on disk)
├── src/
│   ├── loader.py            # Reads PDFs -> chunks.jsonl
│   ├── clean.py             # Filters chunks.jsonl (removes noise)
│   ├── embedder.py          # Generates embeddings -> ChromaDB
│   ├── search.py            # Semantic search (command line)
│   ├── test_search.py       # Validates the search (in-domain vs off-domain)
│   ├── demo.py              # Demo with fixed domain questions
│   └── logging_config.py    # Logging configuration
├── requirements.txt         # Python dependencies
├── .gitignore               # Files ignored by Git
└── README.md                # This file
```

## Installation

### Prerequisites

- Python 3.10+
- Windows, macOS or Linux
- Git (optional)

### Step 1: Get the project

```bash
git clone <your-repository-url>
cd CAPSTONE
```

### Step 2: Create a virtual environment

```bash
python -m venv venv
```

Activate it:

- **Windows (Git Bash):** `source venv/Scripts/activate`
- **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
- **Windows (CMD):** `venv\Scripts\activate.bat`
- **Linux / macOS:** `source venv/bin/activate`

### Step 3: Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

The exact libraries and versions are listed in `requirements.txt`. The key ones are a PDF reader and `chromadb` (vector database, which also ships the embedding model).

## How to run

### Full run (from scratch)

Run the steps **in this order**:

```bash
python src/loader.py      # Reads PDFs and generates chunks
python src/clean.py       # Removes invalid chunks
python src/embedder.py    # Generates embeddings and loads ChromaDB (~5 min)
```

`embedder.py` downloads the embedding model (~80 MB) on its first run and caches it for later runs.

Then search:

```bash
python src/search.py "screen time and obesity in children"
python src/search.py "does screen time affect sleep in children?"
```

### Interactive menu

```bash
python main.py
```

Menu options: search a question, run the full pipeline, run the tests, or exit.

### Quick validation test

Compares a search **inside the domain** against one **outside the domain**:

```bash
python src/test_search.py
```

Result obtained on this project:

```
Query: "screen time and obesity"   -> average distance 0.17
Query: "recipe for chocolate cake" -> average distance 0.76
OK: the domain query returned smaller distances than the unrelated query.
```

If the in-domain distances are clearly smaller, the index is working.

### Demo (several domain questions)

```bash
python src/demo.py
```

Runs a fixed list of questions related to the domain (plus one off-topic control question) and prints, for each result: relevance label, distance, source PDF and chunk number. The relevance labels (High / Medium / Low) are just a friendly reading of the distance; their thresholds are defined in `search.py`.

## Understanding semantic search

### How does it work?

1. **Embeddings:** each text chunk is converted into a vector of numbers (384 dimensions for all-MiniLM-L6-v2). The vector captures the *meaning* of the text.
2. **Index:** all vectors are stored in a vector database (ChromaDB), which allows fast nearest-neighbor lookup.
3. **Search:** the question is converted into a vector with the same model. The system finds the closest vectors using cosine distance.
4. **Result:** the most similar chunks are returned with their distance: **0 means identical meaning**, values near **1 mean unrelated**, and the closer to 0 the more relevant.

### Why is it better than keyword search?

| Keyword search | Semantic search |
|---|---|
| Looks for the exact words | Looks for the meaning |
| "tablet use" does not match "screen time" | "tablet use" is close to "screen time" |
| May return nothing | Returns relevant passages |

### Real example from this project

```
Query:  "is screen time associated with childhood obesity?"

Result #1: PMC13589963.pdf, chunk 0
           "The Association Between Daily Screen Time and Childhood
            Overweight and Obesity: Current Evidence and Potential Mechanisms..."
           Distance: 0.1167  (High relevance)

Query:  "what are the best recipes for chocolate cake?"   (off-topic control)

Result #1: PMC13587429.pdf, chunk 39
           Distance: 0.6830  (Low relevance)
```

Chunk 0 is the first piece of the article (title and authors), which is why it matches a question that is almost identical to the title.

## Main dependencies

- A PDF reading library (text extraction)
- `chromadb`: vector database, also provides the embedding function (all-MiniLM-L6-v2 running on ONNX Runtime)

See `requirements.txt` for the full list.

## Data origin

The 30 PDFs come from **PubMed Central**, an open-access repository of scientific articles. Each article's license allows reuse (typically CC-BY).

Examples of articles in the collection:

- `data/raw/PMC13589963.pdf`: review on daily screen time and childhood overweight and obesity
- `data/raw/PMC13570809.pdf`: artificial intelligence interaction vs. traditional screen exposure in child development
- `data/raw/PMC13589181.pdf`: types of screen time and developmental outcomes in children aged 0-6
- ... (30 in total)

To read an original article, use its PMC ID:

```
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13589963/
```

## Limitations of this delivery (partial)

- No clustering (grouping chunks by topic)
- No anomaly detection
- No text-quality classification
- No graphical interface (terminal only)

These items are planned for the **final delivery**.

## Troubleshooting

### "Collection not found" when running search.py

**Cause:** `embedder.py` has not been run yet, so the index does not exist.

**Fix:**

```bash
python src/embedder.py
```

### Search results look wrong or random

Check, in this order:

1. `embedder.py` ran completely (the last log line shows the total chunks indexed, 6,069 here).
2. `search.py` uses the same collection and embedding function as `embedder.py`.
3. `clean.py` did not remove too many chunks or let noise through.

## Author

**Grazielle Nascimento Ferreira**, Capstone Data Science, 2026.

**Email:** Grazielle.Nascimento0724@jala.university

## License

This project uses data from **PubMed Central** (open access, typically CC-BY).

---

**Last updated:** October 3, 2026
