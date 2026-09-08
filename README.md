## Smart Group Chat Search

An intelligent search system for searching group chat conversations using semantic meaning, keywords, person-based queries, and time-based queries.The system is designed to understand natural-language queries, including Hinglish queries, and return the most relevant chat messages.

## Features

- Semantic search using sentence embeddings
- Keyword-based search using BM25
- Hybrid search combining semantic and keyword relevance
- Person-based / attributed search
- Temporal / date-based search
- Query classification and analysis
- Hinglish query support
- Context retrieval for surrounding conversations
- Top-K ranked search results
- Streamlit-based user interface
- FAISS vector index for efficient similarity search
- Chat data stored using JSON and SQLite

## Project Structure

```text
AI Project/
│
├── app/
│   └── app.py
│
├── data/
│   ├── chat.db
│   └── chat.json
│
├── models/
│   ├── chat_embeddings.npy
│   └── chat.index
│
├── notebooks/
│
├── src/
│   ├── bm25_search.py
│   ├── context_retriever.py
│   ├── database.py
│   ├── generate_chat.py
│   ├── hybrid_search.py
│   ├── query_analyzer.py
│   └── semantic_search.py
│
├── tests/
│
├── .gitignore
├── README.md
└── requirements.txt

# Technologies Used
1. Python
2. Streamlit
3. NumPy
4. Pandas
5. Sentence Transformers
6. FAISS
7. BM25
8. Scikit-learn
9. SQLite
10. Matplotlib
11. Faker

# Search Architecture
 The system follows the pipeline:

                    User Query
                        │
                        ▼
                ┌───────────────┐
                │ Query Analyzer│
                └───────┬───────┘
                        │
                        ▼
                 Query Type
                   Detection
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
       Keyword Search        Semantic Search
          (BM25)                  (FAISS)
             │                     │
             └──────────┬──────────┘
                        ▼
                 Person / Time
                    Filters
                        │
                        ▼
                 Hybrid Search
                        │
                        ▼
                 Score & Ranking
                        │
                        ▼
                   Top-K Results
                        │
                        ▼
              Surrounding Context
                        │
                        ▼
                  Streamlit UI


# Search Types:
1. Semantic Search
Finds messages based on their meaning rather than requiring exact
keyword matches.

Example:

kab Manali jane ka plan tha

The system searches for messages related to the meaning of the query.

2. Attributed Search
Searches for information associated with a particular person.

Example:

what did Priya say about the budget

The system identifies:

Type   : attributed
Person : Priya

and searches for relevant messages from Priya.

3. Temporal Search
Searches messages based on time-related expressions.

Examples:

what did we discuss last month
what did we discuss last week

The query analyzer converts the temporal expression into a date range
before performing the search.

4. Hybrid Search

Hybrid search combines:
BM25 keyword relevance
Semantic similarity

This allows the system to handle both exact keyword matches and
meaning-based matches.

# Query Analyzer

The query analyzer extracts useful information from a user's query.

It identifies:
Query type
Person
Start date
End date

Example 1:
what did Priya say about the budget

Output:
Type       : attributed
Person     : Priya
Start Date : None
End Date   : None

Example 2:
what did we discuss last month

Output:
Type       : temporal
Person     : None
Start Date : ...
End Date   : ...
Data

The project uses chat conversation data containing:
User name
Message
Timestamp

The project stores chat information in:
data/chat.json
data/chat.db

Embeddings and the FAISS index are stored in:
models/chat_embeddings.npy
models/chat.index
Installation
1. Clone or download the project

Open the project folder in VS Code.

2. Create a virtual environment
python -m venv venv
3. Activate the virtual environment

Windows PowerShell:
.\venv\Scripts\Activate.ps1

==>  If the virtual environment is already activated, you can skip this step.

4. Install dependencies
pip install -r requirements.txt

## Running the Project:
Run the Streamlit application from the project root:

Command: streamlit run app/app.py

The application will open in the browser.

Example Queries ->
The application supports queries such as:

kab Manali jane ka plan tha
what did Priya say about the budget
what did we discuss last month
what did we discuss last week
project submission kab hai
budget kitna hai
better processor worth it hai
Search Results

The application displays:

Query type
Top search results
Person who sent the message
Message text
Timestamp
Relevance score
Surrounding conversation context

Results are ranked according to their relevance to the user's query.

# Testing: 
The project was manually tested using different types of queries:

Semantic Queries
kab Manali jane ka plan tha
Attributed Queries
what did Priya say about the budget
Temporal Queries
what did we discuss last month
what did we discuss last week
Additional Queries
budget kitna hai
better processor worth it hai

The search interface successfully returned ranked results for the tested
queries.

# Future Scope
Possible improvements include:

Better Hinglish understanding
Improved temporal expression handling
More advanced query understanding
Conversation summarization
Multi-language support
User authentication
Larger chat datasets
Personalized search
Improved ranking models
LLM-based answer generation
Voice-based search

# Conclusion:

Smart Group Chat Search provides an intelligent way to search large group
chat conversations using natural-language queries.

By combining BM25 keyword search, semantic similarity search, query
analysis, temporal filtering, person-based filtering, and context
retrieval, the system provides more flexible and meaningful conversation
search than traditional keyword-only search.