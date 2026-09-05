import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0,
    max_tokens=4096,
)

response = model.invoke("What is 2 + 2? Answer in one sentence.")

print(response.content)