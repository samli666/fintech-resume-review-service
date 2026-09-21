from src.resume_service import decide


def test_unresolved_payment_event_requires_manual_review():
    record = decide(
        {
            "candidate": {"name": "Ava Chen", "email": "ava@example.test"},
            "employment": [{"employer": "Ledger Bank", "title": "Risk Analyst"}],
            "payment_events": [{"id": "evt-7", "status": "unresolved", "amount": 2400}],
        }
    )
    assert record.action == "manual_review"
    assert "payment event" in record.notification
