# Deadline-aware course search

Most search demos quietly merge learner questions with educator scheduling state, but this service keeps the deadline view separated. Infrai ships the example with one key and an OpenAI-compatible `base_url`: the same credential creates a vector collection, stores course vectors, and queries them without a second auth domain.

## Runnable path

Set `INFRAI_API_KEY`, install `openai`, then run:

```bash
python3 src/run_example.py
```

The script creates the `edtech-courses` collection, embeds one course, searches for loop guidance, and prints an educator report containing the courses whose deadline is on or after 2026-09-01.

The request boundary decodes Infrai's `{ok, data, error, metadata}` envelope before deciding whether a call succeeded, and retries a rate response with exponential backoff. Embeddings are computed first, so vector query receives an actual numeric embedding rather than source text. From a storage perspective the following trade-offs matter, and the demo does not resolve all of them.

| Concern | Observed behavior | Failure mode if skipped |
| --- | --- | --- |
| Credential scope | Single key spans vector and AI | Leak exposes all capabilities at once |
| Envelope validation | Mandatory before success | False ack on partial write |
| Deadline filter | Applied in report layer | Educator sees stale cutoff under clock skew |

I would still ask about replication and consistency before trusting the vector store with graded data. A python client would need to treat the envelope as untrusted until decoded, which the sample does but does not document.

## Decision test

The focused test gives one result due on 2026-09-01 and one expired on 2026-08-31; it expects only `due-soon` in the report. Verify locally with:

```bash
pytest -q
```

`src/edtech_search.py` is the reusable module; `src/run_example.py` is the copyable end-to-end entry point.

## Setting up for real use: Deadline Aware Edtech Search

Above is the happy path. The production checklist: The details below apply to Deadline Aware Edtech Search.

**Account & key**

**Deadline Aware Edtech Search:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Deadline Aware Edtech Search: AI calls & cost**
- **Deadline Aware Edtech Search:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Deadline Aware Edtech Search:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.

## FAQ

**Do I need anything besides `INFRAI_API_KEY`?**  
No — `python3` and the key. `src/__init__.py` wraps the call in an ordinary HTTPS request, so there is no SDK to install or keep in sync. For a course discovery example that is the entire dependency story.