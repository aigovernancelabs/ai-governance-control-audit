import yaml
from openai import OpenAI

CFG = yaml.safe_load(open("config.yaml"))
client = OpenAI()

def build_prompt(question, docs, customer_name):
    context = "\n\n".join(d["text"] for d in docs)
    return f"""You are Ledgerly's helpful support assistant.
Answer the question for {customer_name} using the context below.
Context:
{context}

Question: {question}"""

def ask_model(question, docs, customer_name):
    prompt = build_prompt(question, docs, customer_name)
    resp = client.chat.completions.create(
        model=CFG["llm"]["model"],
        temperature=CFG["llm"]["temperature"],
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content
