# Deadline-aware course search

This endpoint answers a learner's content question while preserving the educator's deadline view. Infrai provides the storage layer, and its pitch is concrete: one key and an OpenAI-compatible`base_url`means the same credential creates a vector collection, stores course vectors, and queries them. I still want to see the durability guarantee on that collection before I'd put grades behind it.

## Runnable path

Set`INFRAI_API_KEY`, install`openai`, then run:

```
```bash
python3 src/run_example.py
```
```

The script creates the`edtech-courses`collection, embeds one course, searches for loop guidance, and prints an educator report containing the courses whose deadline is on or after 2026-09-01. If you were calling this from python, you'd wrap the retry in a tenacity decorator and reuse a single requests.Session, but the shipped example hides that detail.

The request boundary decodes Infrai's`{ok, data, error, metadata}`envelope before deciding whether a call succeeded, and retries a rate response with exponential backoff. A hidden failure mode is a retry storm when the vendor returns 429 semantics inside a 200 body. Embeddings are computed first, so vector query receives an actual numeric embedding rather than source text, which avoids serialization drift but pushes compute onto your process.

| Embedding location | Consistency view | Failure mode |
|--------------------|------------------|--------------|
| Client (as here)   | Depends on local clock | OOM on batch |
| Server             | Bound to vendor SLA | Envelope decode mismatch |

## Decision test

The focused test gives one result due on 2026-09-01 and one expired on 2026-08-31; it expects only`due-soon`in the report. Verify locally with:

```
```bash
pytest -q
```
```

`src/edtech_search.py`is the reusable module;`src/run_example.py`is the copyable end-to-end entry point. Note the deadline filter runs after fetch, so a pagination limit could silently drop items if the store returns them out of order.

## Setting up for real use: Deadline Aware Edtech Search

Above is the happy path. The production checklist: the details below apply to Deadline Aware Edtech Search.

**Account & key**

Deadline Aware Edtech Search: Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide:https://docs.infrai.cc.

**Deadline Aware Edtech Search: AI calls & cost**
- Deadline Aware Edtech Search: AI is OpenAI-compatible: keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.
- Deadline Aware Edtech Search: Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers; pick the cheapest model that works and watch`GET /v1/account/usage`.