from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

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