import sys
from pathlib import Path
import streamlit as st

# Allow importing files from src
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

sys.path.append(str(SRC_DIR))

from hybrid_search import (
    load_messages,
    build_bm25,
    hybrid_search,
    get_context,
    MODEL_NAME
)

from sentence_transformers import SentenceTransformer
import faiss


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Group Chat Search",
    page_icon="💬",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.main-title {
    font-size: 40px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    color: #777;
    font-size: 18px;
    margin-bottom: 25px;
}

.result-box {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #ddd;
    margin-bottom: 15px;
}

.message {
    font-size: 20px;
    font-weight: 600;
}

.context-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #f5f5f5;
    margin-top: 10px;
}

.highlight {
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD SYSTEM
# ============================================================

@st.cache_resource
def load_system():

    messages = load_messages()

    bm25 = build_bm25(messages)

    model = SentenceTransformer(MODEL_NAME)

    index_file = BASE_DIR / "models" / "chat.index"

    faiss_index = faiss.read_index(str(index_file))

    return messages, bm25, model, faiss_index


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">💬 Smart Group Chat Search</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Search your conversations by meaning, person, or time — even in Hinglish.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# LOAD
# ============================================================

try:

    messages, bm25, model, faiss_index = load_system()

except Exception as e:

    st.error("Could not load the search system.")

    st.code(str(e))

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🔎 Search Options")

    top_k = st.slider(
        "Number of results",
        1,
        10,
        5
    )

    st.markdown("---")

    st.markdown("### Try these")

    st.write("• when did we decide on the trip")

    st.write("• what did Priya say about the budget")

    st.write("• what did we discuss last month")

    st.write("• Manali trip")


# ============================================================
# SEARCH BOX
# ============================================================

query = st.text_input(
    "Search your group chat",
    placeholder="e.g. when did we decide on the trip?"
)


search_clicked = st.button(
    "🔍 Search",
    use_container_width=True
)


# ============================================================
# SEARCH
# ============================================================

if search_clicked and query.strip():

    with st.spinner("Searching 5,000 messages..."):

        results = hybrid_search(
            query,
            messages,
            bm25,
            model,
            faiss_index,
            top_k=top_k
        )


    # --------------------------------------------------------
    # QUERY TYPE
    # --------------------------------------------------------

    query_lower = query.lower()

    if "what did" in query_lower and "say" in query_lower:

        query_type = "Attributed Search"

    elif (
        "last month" in query_lower
        or "this month" in query_lower
        or "last week" in query_lower
        or "yesterday" in query_lower
    ):

        query_type = "Temporal Search"

    else:

        query_type = "Semantic Search"


    st.markdown("---")

    st.subheader("Search Analysis")

    st.info(f"Query Type: **{query_type}**")


    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    if not results:

        st.warning("No matching messages found.")

    else:

        st.subheader(
            f"Top {len(results)} Results"
        )


        for rank, result in enumerate(results, start=1):

            with st.container():

                st.markdown(
                    f"""
                    <div class="result-box">

                    <div class="message">
                    ⭐ #{rank} &nbsp; {result['sender']}
                    </div>

                    <p>
                    <b>{result['text']}</b>
                    </p>

                    <small>
                    🕒 {result['timestamp']}
                    &nbsp;&nbsp; | &nbsp;&nbsp;
                    Score: {result['hybrid_score']:.3f}
                    </small>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


                # ------------------------------------------------
                # CONTEXT
                # ------------------------------------------------

                if rank == 1:

                    context = get_context(
                        messages,
                        result,
                        context_size=5
                    )

                    with st.expander(
                        "💬 Show surrounding conversation",
                        expanded=True
                    ):

                        for message in context:

                            if message["id"] == result["id"]:

                                st.markdown(
                                    f"""
                                    ⭐ **{message['sender']}**
                                    
                                    {message['text']}
                                    
                                    `{message['timestamp']}`
                                    """
                                )

                            else:

                                st.markdown(
                                    f"""
                                    **{message['sender']}**
                                    
                                    {message['text']}
                                    
                                    `{message['timestamp']}`
                                    """
                                )

                            st.divider()