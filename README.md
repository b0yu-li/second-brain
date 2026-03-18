# README

## Todos

+ [x] Ingest Contacts
  + [x] Prep. the contacts
+ [x] Remember the history (persistent memory)
+ [x] Test drive the RAG
+ [x] Try ClaudeAI
+ [x] Evaluations
  + [x] Basic Evaluations
  + [ ] Test if can remember the history (if chat history persisted)
+ [x] Telemetry
  + [x] PoC
  + [x] Trace Status: UNSET, `add_span_processor` order
+ [ ] Q: When I add new content in the `/data`, should I delete the files in `/db` folder and re-ingest the knowledge base?
+ [ ] Inflate README.md
+ [ ] Make a video to showcase it
+ [ ] Blog

## Demo Structure
+ Can remember the history
+ Evaluations
+ Telemetry

## Commands to Interact

+ Ingest the data:

```shell
uv run python src/ingest.py
```

+ Ask the second brain

```shell
uv run python main.py
```

### Evaluations

```shell
uv run python -m src.eval
```

### Arize Phoenix Telemetry

```shell
uvx arize-phoenix serve
```
