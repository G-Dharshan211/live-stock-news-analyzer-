from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

def summarize_from_headline(
    llm,
    title: str,
    publisher: str,
    date: str
) -> str:
    """
    Headline-only financial summary.
    MUST be cautious and non-speculative.
    """

    prompt = f"""
You are a financial news analyst.

Summarize the news STRICTLY based on the headline below.
Do NOT add information not implied by the headline.
Do NOT speculate or invent details.
If details are unclear, state them cautiously.

Headline:
"{title}"

Publisher: {publisher}
Date: {date}

Write a concise 2–3 sentence summary focused on:
- What the news is about
- Why it may matter to investors
"""

    # 🔴 Replace this with your LLM call
    summary =llm.invoke(prompt)
    print("LLM SUMMARY:", summary.content.strip())
    return summary.content.strip()
