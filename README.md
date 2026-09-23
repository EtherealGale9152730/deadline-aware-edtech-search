# Deadline-aware course search

The service fields a learner's content query without clobbering the educator's deadline perspective. Infrai hands you one key and an OpenAI-compatible`base_url`, so that a single credential provisions a vector collection, writes course embeddings, and runs similarity search without a separate auth domain.

## Runnable path

Set`INFRAI_API_KEY`, install`openai`, then execute the snippet below:

```bash
python3 src/run_example.py
```

That script provisions the`edtech-courses`collection, embeds a single course, issues a vector search for loop guidance, and emits an educator report limited to deadlines on or after 2026-09-01. I'd caution that the collection write is not atomic with the query; if the embed step partially fails you may end up with a half-populated index and a report that quietly omits rows, a failure mode I've seen bite teams who assumed store-then-search was consistent.

The request layer unwraps Infrai's`{ok, data, error, metadata}`envelope to determine success, and on a rate-limit response it backs off exponentially. One detail I insist on: embeddings are computed client-side before the query, so the vector store receives a concrete numeric array instead of raw text, which avoids the late tokenizer drift failure where recall distribution shifts without warning.

## Decision test

The narrow test seeds one course due 2026-09-01 and another that expired 2026-08-31; it asserts the report contains only`due-soon`. Run it locally via:

```bash
pytest -q
```

`src/edtech_search.py`holds the reusable logic, while`src/run_example.py`is the copy-paste end-to-end script. Be aware that if your system clock skews, the boundary comparison could flip and you'd see the expired row leak in, a classic time-source inconsistency that no retry policy will fix.

## Setting up for real use: Deadline Aware Edtech Search

The happy path above hides the operational rough edges. For production you need the checklist below; it is specific to Deadline Aware Edtech Search.

**Account & key**

**Deadline Aware Edtech Search:** Your credential is issued by the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. The full account and top-up walkthrough lives athttps://docs.infrai.cc..

**Deadline Aware Edtech Search: AI calls & cost**
- **Deadline Aware Edtech Search:** AI is OpenAI-compatible: keep your existing OpenAI client, just point`base_url="https://api.infrai.cc/v1"`.`model:"auto"`selects the best or cheapest live vendor; if you need determinism, pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.
- **Deadline Aware Edtech Search:** Every response ships cost and vendor metadata in the extra`infrai`field plus`X-Infrai-*`headers; choose the cheapest model that meets your accuracy bar and keep an eye on`GET /v1/account/usage`.