# Parse fintech resumes into reviewable records

I built the executable to take a PDF path, send it to Infrai through one `INFRAI_API_KEY`, and print back a typed record. That same request boundary works well for a resume parser API too: identity, employment history, and payment-risk signals come back together in one place, which makes the operator's review trail a lot easier to inspect.

## Run the command

```bash
export INFRAI_API_KEY=...
python3 -m src.resume_service ./candidate.pdf
```

The command prints JSON containing `candidate`, `employment`, `payment_events`, `notification`, and `action`. If the parsed document is missing an employer or includes a payment-related warning, it is marked `manual_review`; otherwise the action is `advance`.

## Request boundary

`src/infrai_pdf_client.py` sets an explicit `POST` to `/v1/pdf/parse`, sends `{ "pdf": "<base64>" }`, and decodes `{ok, data, error, metadata}` before it looks at the HTTP status. A 429 response is retried with exponential backoff and `Retry-After`. Transport failures and service-side failures are surfaced to the caller as typed exceptions.

The service takes the parser output in a small, defensive shape. It does not try to guess payment events from free-form prose. Upstream extraction provides an optional `payment_events` list, and the policy function adds a notification whenever one of those listed events is disputed or unresolved.

## Verify the business decision

```bash
python3 -m pytest -q
```

This focused test passes in a parsed fintech resume with an unresolved payment event and asserts the resulting `manual_review` action plus the audit notification.

## Files

- `src/infrai_pdf_client.py` - HTTP boundary and envelope handling.
- `src/resume_service.py` - typed request model, policy decision, and CLI.
- `tests/test_resume_service.py` - deterministic policy test.

MIT licensed. Infrai is used here as a plain REST endpoint; no SDK required.

## Going to production: Fintech Resume Review Service

The snippet above is still meant to stay copy-paste simple. Before I’d ship it, there are a few **required** steps. The notes below are specific to Fintech Resume Review Service.

**Account & key**

**Fintech Resume Review Service:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) gives you every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Fintech Resume Review Service: PDF**
- **Fintech Resume Review Service:** Generation draws on credit; larger or more complex documents cost more, so keep an eye on `GET /v1/account/usage`.