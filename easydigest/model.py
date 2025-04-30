!pip install openai
import openai

client = openai.OpenAI(api_key= "YOUR_API_KEY")

#retrieval

import requests
import re
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity

#1. Find context sentences in the article
def find_sentence_with_word(article_text, word):
    sentences = re.split(r'(?<=[.!?])\s+|\n+', article_text)
    for sentence in sentences:
        if word in sentence:
            return sentence.strip()
    return ""

#2. Get candidate definition titles from wiki
def search_wikipedia_candidates(word):
    url = "https://ko.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": word,
        "format": "json"
    }
    res = requests.get(url, params=params)
    if res.status_code == 200:
        return [entry["title"] for entry in res.json()["query"]["search"]]
    return []

#3. Scraping wiki definitions for each title
def retrieve_definition(title):
    url = f"https://ko.wikipedia.org/api/rest_v1/page/summary/{title}"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json().get("extract", "")
    return ""

# 4. Compare the similarity between context sentences and definitions to select the most appropriate definition.
model = SentenceTransformer('jhgan/ko-sbert-nli')  
# Solving polysemy and homonym problems by considering the meaning of sentences through sentence embedding using Korean SBERT

def select_best_definition(context_sentence, definitions):
    embeddings = model.encode([context_sentence] + definitions)
    similarities = util.cos_sim(embeddings[0], embeddings[1:])[0]
    best_idx = similarities.argmax()
    return definitions[best_idx]

#If the word is not found, search in gpt
def generate_definition_with_gpt(word):
    prompt = f"{word}라는 용어의 정의가 너무 궁금해.초등학생도 이해할 수 있도록 쉽고 간단하게 설명해줘."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 사전을 대신해주는 지식 AI야."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"[GPT error]: {str(e)}"


#generation

def simplify_with_gpt(definition, word):
    prompt = f"""
'{word}'는 다음과 같은 뜻을 가지고 있어:
\"{definition}\"

이걸 초등학생도 이해할 수 있도록 아주 쉽게 설명해줘. 짧고 자연스럽게 부탁해.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 초등학생에게 복잡한 말을 쉽게 설명해주는 도우미야."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"[GPT error]: {str(e)}"


# 5. full execution function (final output function)
def explain_word_in_context(article, word):
    print(f"\n[terminology] {word}")

    context = find_sentence_with_word(article, word)
    if not context:
        return "No sentences containing that word were found."

    print(f"\n[context]\n{context}")

    titles = search_wikipedia_candidates(word)
    print(f"\n[definition titles]\n{titles[:5]}")

    definitions = [retrieve_definition(title) for title in titles[:5]]
    definitions = [d for d in definitions if len(d) > 20]  # Excluding definitions that are too short

    if definitions:
        best_def = select_best_definition(context, definitions)
        print(f"\n[selected definition]\n{best_def}")
    else:
        print("\nDefinition is missing or insufficient in Wikipedia → Try creating it with GPT")
        best_def = generate_definition_with_gpt(word)
        print(f"\n[GPT creation definition]\n{best_def}")

    # Generation step
    simplified = simplify_with_gpt(best_def, word)
    print(f"\n[easy explanation]\n{simplified}")

    return simplified
