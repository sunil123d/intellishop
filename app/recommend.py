# app/recommend.py
"""
LangChain-powered recommendation engine.
Takes search results and generates a natural language
recommendation explaining WHY these products fit.
"""

# app/recommend.py
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import GROQ_API_KEY, GROQ_MODEL


# ── Build the LangChain pipeline ────────────────────────────────
llm = ChatGroq(
    api_key     = GROQ_API_KEY,
    model       = GROQ_MODEL,
    temperature = 0.3
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert shopping assistant.
Given a customer's search query and a list of matching products,
write a friendly 2-3 sentence recommendation explaining which
products best fit their needs and why. Be specific about
features, price, or ratings that matter."""),
    ("user", """Customer searched for: {query}

Matching products:
{products}

Write a helpful recommendation:""")
])

# LangChain "chain" — pipes prompt → LLM → text output
# This | syntax is called LCEL (LangChain Expression Language)
chain = prompt | llm | StrOutputParser()


def generate_recommendation(query: str, products: list) -> str:
    """
    Uses LangChain to generate a natural language
    recommendation based on search results.
    """
    if not products:
        return "No matching products found for your search."

    products_text = "\n".join([
        f"- {p['name']} (₹{p['price']}, "
        f"{p['rating']}★, {p['category']}): {p['description'][:100]}"
        for p in products
    ])

    recommendation = chain.invoke({
        "query":    query,
        "products": products_text
    })

    return recommendation