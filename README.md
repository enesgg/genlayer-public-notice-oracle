# GenLayer Public Notice Oracle

A reusable **GenLayer Intelligent Contract** for source-grounded verification of public web notices.

The contract accepts an HTTPS public source and a factual question. The leader extracts a small structured decision, while validators **independently inspect the same source** before accepting it. For decisive results, the stored evidence must be an exact quote that also appears in a validator's independently fetched copy of the page.

## Why this primitive matters

Public rules and notices change frequently and are often copied into stale secondary sources. Applications need a way to make a small, auditable decision from a primary notice without trusting a single LLM response.

Useful cases include:

- application or registration deadlines;
- eligibility requirements;
- filing fees and required documents;
- whether a notice explicitly announces a status change;
- policy or service availability checks;
- other factual questions that can be grounded in one public source.

This is intentionally a **standalone contract primitive**, not a frontend app, simple storage example, or generic "AI decides X" demo.

## Consensus design

`verify_notice(record_id, source_url, question)` uses a custom leader/validator flow with `glvm.run_nondet_unsafe`:

1. **Deterministic gate** — validates the record ID, HTTPS URL, input sizes, and duplicate protection.
2. **Leader extraction** — renders the source, treats it as untrusted evidence, and returns only:
   - `verdict`: `supported`, `contradicted`, or `unclear`;
   - `evidence`: an exact contiguous quote from the page for decisive verdicts.
3. **Independent validator derivation** — every validator re-runs the source inspection and must derive the same verdict.
4. **Independent evidence grounding** — for `supported` / `contradicted`, the validator fetches the source again and verifies that both the leader and validator evidence quotes occur in that independently fetched page text.
5. **Fail closed** — malformed results, missing evidence, external uncertainty, or validator exceptions disagree rather than implicitly accepting the leader.

This means consensus verifies the **substance** of the stored decision rather than merely checking JSON shape.

## State design

Each accepted verification is immutable under a caller-supplied `record_id`:

```text
Verification
├── record_id
├── source_url
├── question
├── verdict        # supported | contradicted | unclear
└── evidence       # exact source quote for decisive verdicts
```

The contract also stores the latest record ID and total successful verifications. Duplicate IDs are rejected so an existing verification cannot be silently overwritten.

## Public API

- `verify_notice(record_id, source_url, question)` — consensus-backed source verification.
- `get_record(record_id)` — read a stored verification.
- `get_latest_record()` — read the most recent verification.
- `get_total_verifications()` — read the successful verification count.

## Example

```text
record_id: permit-deadline-2026
source_url: https://authority.example/permit-notice
question: Does the notice say applications close on 30 September 2026?
```

Possible accepted state:

```json
{
  "record_id": "permit-deadline-2026",
  "source_url": "https://authority.example/permit-notice",
  "question": "Does the notice say applications close on 30 September 2026?",
  "verdict": "supported",
  "evidence": "Applications close on 30 September 2026."
}
```

See [`examples/example_usage.md`](examples/example_usage.md) for more scenarios.

## Testing

Direct-mode tests cover:

- empty initial state;
- successful verification and state persistence;
- independent validator disagreement when verdicts differ;
- rejection when evidence is not present in the independently fetched source;
- duplicate record protection;
- HTTPS enforcement;
- malformed verdict rejection.

With GenLayer's testing stack installed:

```bash
pytest tests/direct/ -v
```

Before deployment/submission, lint the contract:

```bash
genvm-lint check contracts/public_notice_oracle.py
```

A Studio/testnet pass is recommended after direct tests to exercise real multi-validator consensus.

## Security properties

- HTTPS-only sources.
- Source content is explicitly treated as untrusted data to reduce prompt-injection risk.
- Validators independently derive the verdict instead of trusting the leader.
- Decisive evidence must be source-grounded on the validator's own fetch.
- `unclear` is a first-class outcome so insufficient evidence does not get forced into a yes/no result.
- Validation fails closed on exceptions or malformed data.
- State records are append-only by unique record ID.

## License

MIT
