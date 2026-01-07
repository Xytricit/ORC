"""Simple natural language query parser stub."""


def parse_query(text: str):
    return {"keywords": text.lower().split()}
