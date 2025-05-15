# Download Stanza Korean model
import stanza
stanza.download('ko')

import requests
import stanza
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

import openai

client = openai.OpenAI(api_key= "YOUR_KEY")

#retrieval

# — Stanza Korean pipeline (tokenize + pos)
nlp = stanza.Pipeline(lang='ko', processors='tokenize,pos', use_gpu=False)

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

# 2) POS Analysis with Stanza
def analyze_pos_with_stanza(word: str):
    doc = nlp(word)
    return [(w.text, w.upos) for sent in doc.sentences for w in sent.words]

# 3) Final part of speech decision (based on upos)
def infer_overall_pos(tokens):
    upos = [p for _, p in tokens]
    if any(p == 'VERB' for p in upos):
        return 'Verb'
    if any(p == 'ADJ' for p in upos):
        return 'Adjective'
    if any(p == 'ADV' for p in upos):
        return 'Adverb'
    if any(p == 'NOUN' for p in upos):
        return 'Noun'
    return 'Unknown'

# 4) Stanza-based stem extraction
#    Stanza also provides a lemma, but the Korean model does not have a lemma, so we use the longest token.
def get_lemma(word: str):
    toks = analyze_pos_with_stanza(word)
    return max(toks, key=lambda x: len(x[0]))[0]

# 5) Wiki definition lookup
def retrieve_definition(word: str) -> str:
    for key in (word, get_lemma(word)):
        url = f"https://ko.wikipedia.org/api/rest_v1/page/summary/{key}"
        r = requests.get(url)
        if r.status_code == 200:
            ex = r.json().get("extract", "").strip()
            if ex:
                return ex
    return ""

# 6) Create definition in GPT if not found in Wikipedia (fallback)
def generate_definition_with_gpt(word: str) -> str:
    prompt = f"'{word}'라는 단어의 정의를 명확하게 설명해 주세요. 백과사전 스타일로."
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system","content":"당신은 단어 정의 전문가입니다."},
            {"role":"user","content":prompt}
        ],
        max_tokens=1024, temperature=0.7
    )
    return res.choices[0].message.content.strip()

#generation

def simplify_with_gpt(defn: str, word: str) -> str:
    prompt = (
        f"'{word}'는 다음과 같은 뜻을 가지고 있어:\n"
        f"\"{defn}\"\n\n"
        "이걸 초등학생도 이해할 수 있도록 아주 쉽게 설명하고, 존댓말로 설명해 주세요. 그리고 짧고 자연스럽게 부탁해요."
    )
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system","content":"너는 초등학생에게 복잡한 말을 쉽게 설명해주는 도우미야."},
            {"role":"user","content":prompt}
        ],
        max_tokens=512, temperature=0.7
    )
    return res.choices[0].message.content.strip()

# full execution function (final output function)
def retrieval_and_summarize(article: str, word: str):
    print("\n[Article Summary]\n", summarize_article(article))

    toks = analyze_pos_with_stanza(word)
    #print("\n[Morphs + POS]\n", toks)

    overall = infer_overall_pos(toks)
    print(f"[Overall POS] {word}: {overall}")

    definition = retrieve_definition(word)
    if not definition:
        definition = generate_definition_with_gpt(word)
        print("\n[GPT Definition]\n", definition)
    else:
        print("\n[Wikipedia Definition]\n", definition)

    print("\n[Easy Explanation]\n", simplify_with_gpt(definition, word))

# test
if __name__ == "__main__":
    article = input("Enter article text:\n")
    word = input("Enter word to look up:\n")
    retrieval_and_summarize(article, word)
