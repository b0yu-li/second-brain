# README

## Todos

+ [x] Ingest Contacts
  + [x] Prep. the contacts
+ [x] Remember the history (persistent memory)
+ [ ] Test drive the RAG
+ [ ] Evaluations
+ [ ] Q: When I add new content in the `/data`, should I delete the files in `/db` folder and re-ingest the knowledge base?

## Commands to Interact

+ Ingest the data:

```shell
uv run python src/ingest.py
```

+ Ask the second brain

```shell
uv run python main.py
```
