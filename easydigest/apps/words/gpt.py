import requests
import stanza
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import openai

# OpenAI 클라이언트 초기화
client = openai.OpenAI(api_key="YOUR_OPEN_KEY")

# 우리말샘 API 키
API_KEY = "API_KEY"

# ─── retrieval ────────────────────────────────────────────────────────────

# Stanza Korean pipeline (tokenize + pos)
nlp = stanza.Pipeline(lang="ko", processors="tokenize,pos", use_gpu=False)

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

# 2) POS Analysis with Stanza
def analyze_pos_with_stanza(word: str):
    doc = nlp(word)
    return [(w.text, w.upos) for sent in doc.sentences for w in sent.words]

# 3) Final part of speech decision (based on upos)
def infer_overall_pos(tokens):
    upos = [p for _, p in tokens]
    if any(p == "VERB" for p in upos):
        return "Verb"
    if any(p == "ADJ" for p in upos):
        return "Adjective"
    if any(p == "ADV" for p in upos):
        return "Adverb"
    if any(p == "NOUN" for p in upos):
        return "Noun"
    return "Unknown"

# 4) Stanza-based stem extraction
def get_lemma(word: str):
    toks = analyze_pos_with_stanza(word)
    return max(toks, key=lambda x: len(x[0]))[0]

# 5) Load 우리말샘
def retrieve_definition(word: str) -> str:
    search_url = "https://stdict.korean.go.kr/api/search.do"
    params = {
        "key":      API_KEY,
        "q":        word,
        "req_type": "json",
        "start":    1,
        "num":      10
    }

    try:
        resp = requests.get(search_url, params=params, timeout=5)
        resp.raise_for_status()
    except Exception as e:
        print(f"[Error] 우리말샘 API 호출 실패: {e}")
        return ""

    try:
        data = resp.json()
    except ValueError:
        print("[Error] 우리말샘 응답이 JSON이 아닙니다.")
        return ""

    items = data.get("channel", {}).get("item", [])
    if not items:
        return ""

    raw_sense = items[0].get("sense", None)
    if not raw_sense:
        return ""

    if isinstance(raw_sense, list) and raw_sense:
        return raw_sense[0].get("definition", "").strip()
    if isinstance(raw_sense, dict):
        return raw_sense.get("definition", "").strip()

    return ""


# 6) If there is no definition in 우리말샘, create it with GPT (context-based)
def generate_definition_with_gpt(word: str, context_sentence: str) -> str:

    prompt = (
        f"아래 문장에서 '{word}'라는 단어가 쓰였어요:\n"
        f"  {context_sentence}\n\n"
        "이 문맥만 보고, “기사에서는 이 단어가 무엇을 의미하는지” 백과사전 스타일로 설명해 주세요. "
        "다른 사례나 의견 없이, 오로지 이 문장 기준으로만 정의해 주시면 됩니다."
    )
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 전문 용어 정의 전문가입니다."},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=150,
        temperature=0.0
    )
    return res.choices[0].message.content.strip()

# ─── generation ───────────────────────────────────────────────────────────

def simplify_with_gpt(defn: str, word: str, context_sentence: str) -> str:

    prompt = (
        f"아래 정의에 따라 '{word}'라는 단어가 있습니다:\n"
        f"  \"{defn}\"\n\n"
        f"그리고 이 문장에서 '{word}'가 이렇게 쓰였어요:\n"
        f"  {context_sentence}\n\n"
        "이 기사의 맥락을 고려해서, “이 단어가 이 기사 문맥에서 어떤 의미로 사용되었는지”만 말씀해주시고, 단어 직접 언급하지말고 계속 '이 단어' 이런식으로 말씀해주세요"
        "초등학생도 알 수 있게 쉽고 정중한 말투(존댓말)로 설명해 주세요. "
        "기자의 의견이나 판단, 기사 내용 전체 요약은 빼고, '이 단어가 뜻하는 바'만 말씀해 주시면 됩니다."
        "단어를 직접 언급하는 것이 아니라 '이 단어는' 이런식으로 말씀해주세요."
        
    )
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 어린이에게 친절하고 정중하게 설명해 주는 선생님이야."},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=512,
        temperature=0.7
    )
    return res.choices[0].message.content.strip()



# full execution function (final output function)
def retrieval_and_summarize(article: str, word: str):
    # 1) Article summary
    raw_summary = summarize_article(article)
    #print("\n[Article Summary]\n", summarize_article(article))

    # 1-2) Refining the summary with GPT
    polished_summary = refine_summary_with_gpt(raw_summary)
    print("\n[Article Summary]\n", polished_summary)

    # 2) POS analysis
    toks    = analyze_pos_with_stanza(word)
    overall = infer_overall_pos(toks)
    print(f"[Overall POS] {word}: {overall}")

    # 3) Get definition (우리말샘 → GPT fallback)
    definition = retrieve_definition(word)

    #Extract the first sentence containing the word in the article sentences
    context_sentence = ""
    for sent in article.split("."):
        if word in sent:
            context_sentence = sent.strip() + "."
            break
    if not context_sentence:
        context_sentence = article.split(".")[0].strip() + "."

    if not definition:
        print("\n[Info] 우리말샘에 정의가 없어, 기사 문맥으로 GPT로 정의를 생성합니다.\n")
        # Generate definition dynamically by passing 'word' and 'context_sentence' to generate_definition_with_gpt
        definition = generate_definition_with_gpt(word, context_sentence)
        print("[GPT Definition]\n", definition)
    else:
        print("\n[우리말샘 Definition]\n", definition)

    # 4) Easy context explanation
    easy = simplify_with_gpt(definition, word, context_sentence)
    print("\n[Easy Explanation]\n", easy)

# test
if __name__ == "__main__":
    article = input("Enter article text:\n")
    word    = input("Enter word to look up:\n")
    retrieval_and_summarize(article, word)
