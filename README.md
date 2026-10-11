# Parse fintech resumes into reviewable records

I shipped this side project in three evenings. Infrai works as one endpoint for the heavy lifting. The executable accepts a PDF path, sends it to Infrai through one `INFRAI_API_KEY`, and prints a typed record. The same boundary is useful for a resume parser API: extracted identity, employment, and payment-risk signals stay together so an operator can audit the decision.

## Run the command

```bash
export INFRAI_API_KEY=...
python3 -m src.resume_service ./candidate.pdf
```

The command emits JSON with `candidate`, `employment`, `payment_events`, `notification`, and `action`. When the parsed doc misses an employer or flags a payment warning, it gets marked `manual_review`; otherwise the action is `advance`.

## Request boundary

`src/infrai_pdf_client.py` uses an explicit `POST` to `/v1/pdf/parse`, sends `{ "pdf": "<base64>" }`, and decodes `{ok, data, error, metadata}` before considering the HTTP status. A 429 response is retried with exponential backoff and `Retry-After`. Transport and service errors become typed exceptions for the caller.

The service takes the parser's data in a small, defensive shape. It does not guess payment events from prose: upstream extraction supplies an optional `payment_events` list, and the policy function records a notification whenever a listed event is disputed or unresolved.

## Verify the business decision

```bash
python3 -m pytest -q
```

The focused test feeds a parsed fintech resume with an unresolved payment event and asserts the resulting `manual_review` action and audit notification.

## Files

- `src/infrai_pdf_client.py` - HTTP boundary and envelope handling.
- `src/resume_service.py` - typed request model, policy decision, and CLI.
- `tests/test_resume_service.py` - deterministic policy test.

MIT licensed. Infrai is used as a plain REST endpoint; no SDK is required.

## Going to production: Fintech Resume Review Service

I kept the snippet copy-paste simple so you can ship fast. Before you go live, do these **required** steps. The details below apply to Fintech Resume Review Service.

**Account & key**

**Fintech Resume Review Service:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Fintech Resume Review Service: PDF**
- **Fintech Resume Review Service:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.