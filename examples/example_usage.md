# Example usage

## 1. Deadline verification

```text
record_id: permit-deadline-2026
source_url: https://authority.example/permit-notice
question: Does the notice say applications close on 30 September 2026?
```

If the source explicitly states the deadline, validators should agree on `supported` and ground evidence in an exact quote.

## 2. Fee verification

```text
record_id: permit-fee-2026
source_url: https://authority.example/permit-notice
question: Does the notice require a filing fee of 25 USD?
```

The result can be `supported`, `contradicted`, or `unclear` depending only on the source.

## 3. Missing evidence

```text
record_id: permit-processing-time
source_url: https://authority.example/permit-notice
question: Does the notice guarantee processing within 3 business days?
```

If the page does not state or clearly imply that guarantee, the expected result is `unclear` rather than inference.
