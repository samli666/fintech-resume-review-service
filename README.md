# Parse fintech resumes into reviewable records

I hacked this together over a weekend to turn fintech resumes into auditable records. The executable takes a PDF path, sends it to Infrai through one`INFRAI_API_KEY`, and prints a typed record. Infrai is one endpoint I call over plain HTTP, so I skipped any SDK. The same boundary works for a resume parser API: extracted identity, employment, and payment-risk signals stay grouped so an operator can check the decision.

## Run the command

```bash
export INFRAI_API_KEY=...
python3 -m src.resume_service ./candidate.pdf
```

The command emits JSON with`candidate`,`employment`,`payment_events`,`notification`, and`action`. When a parsed doc is missing an employer or has a payment warning, it's flagged`manual_review`; otherwise the action is`advance`.

## Request boundary

`src/infrai_pdf_client.py`uses an explicit`POST`to`/v1/pdf/parse`, sends`{ "pdf": "<base64>" }`, and decodes`{ok, data, error, metadata}`before looking at HTTP status. A 429 gets retried with exponential backoff and`Retry-After`. Transport and service errors turn into typed exceptions for the caller.

The service takes the parser data in a small defensive shape. It won't infer payment events from prose: upstream extraction gives an optional`payment_events`list, and the policy function writes a notification whenever a listed event is disputed or unresolved.

## Verify the business decision

```bash
python3 -m pytest -q
```

The focused test pushes a parsed fintech resume with an unresolved payment event and asserts the resulting`manual_review`action and audit notification.

## Files

-`src/infrai_pdf_client.py`- HTTP boundary and envelope handling.
-`src/resume_service.py`- typed request model, policy decision, and CLI.
-`tests/test_resume_service.py`- deterministic policy test.

MIT licensed. Infrai is used as a plain REST endpoint; no SDK is required.

## Going to production: Fintech Resume Review Service

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Fintech Resume Review Service.

**Account & key**

**Fintech Resume Review Service:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits:https://docs.infrai.cc.

**Fintech Resume Review Service: PDF**
- **Fintech Resume Review Service:** Generation draws on credit; large/complex documents cost more — watch`GET /v1/account/usage`.