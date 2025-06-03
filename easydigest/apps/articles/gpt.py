from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import openai
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY")

# OpenAI client initialization
client = openai.OpenAI(api_key=OPENAI_KEY)

# Load KoBART model (for Korean article summary)
kobart_tokenizer = AutoTokenizer.from_pretrained("gangyeolkim/kobart-korean-summarizer-v2")
kobart_model     = AutoModelForSeq2SeqLM.from_pretrained("gangyeolkim/kobart-korean-summarizer-v2")

# 1) Article summary function
def summarize_article(text: str) -> str:
    inputs = kobart_tokenizer(text, max_length=1024, return_tensors="pt", truncation=True)
    ids = kobart_model.generate(
        inputs["input_ids"],
        max_length=300,
        min_length=100,
        num_beams=4,
        no_repeat_ngram_size=2,
        early_stopping=True
    )
    return kobart_tokenizer.decode(ids[0], skip_special_tokens=True)

# 1-1) GPT summary polish (sentence structure and spacing supplement)
def refine_summary_with_gpt(raw_summary: str) -> str:

    prompt = (
        "아래는 코바트(KoBART) 모델이 생성한 한국어 요약문입니다.\n\n"
        f"\"{raw_summary}\"\n\n"
        "이 요약문을 존댓말로 유지하면서, 문장 흐름과 띄어쓰기를 매끄럽게 고쳐 주세요. "
        "불필요한 중복이나 어색한 표현은 삭제하고, 핵심 내용은 그대로 살려 주세요."
    )
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 한국어 문장을 자연스럽게 다듬어 주는 전문가입니다."},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=400,
        temperature=0.0
    )
    return res.choices[0].message.content.strip()
