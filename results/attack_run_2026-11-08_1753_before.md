# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-08 17:53
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `7aa98818-2a6e-47cf-93ce-287960835c6e` | placeholder | 0.000 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `eef2221a-7a0d-4f3d-b4cc-f9632f96892a` | placeholder | 0.000 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `117ef0c2-28c9-43a9-b0cc-ebc2631be264` | placeholder | 0.000 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `1f690118-a942-4b53-8875-84972a6b20ce` | placeholder | 0.000 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `59c1a456-8528-49a0-8ccd-0899ce9944af` | placeholder | 0.000 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `ac453db7-09e6-4cd8-92f4-e9db8019075c` | placeholder | 0.000 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `7e0715ac-e7a0-46f4-9b86-f13cbce1c33e` | placeholder | 0.000 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `6e6d9f02-3b37-4ad0-acbf-ff2396d98cd5` | placeholder | 0.000 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `cc4b62d6-8db7-4518-ac9b-d2f537f3d61a` | placeholder | 0.000 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `1de5aa9a-a259-46ec-9ee2-c36f99af85cd` | placeholder | 0.000 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `56e1a1eb-9f16-42c3-a46c-dea121a9d8fc` | placeholder | 0.000 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `e07cf781-4b0b-4fa0-8128-c0f7823ac7e9` | placeholder | 0.000 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `24c7503c-486b-40cf-9b06-eb8c5f20574b` | placeholder | 0.000 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c0420ff4-2a90-407b-938b-7ff340e74aa3` | placeholder | 0.000 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `d9f7573e-0e7b-4b27-b640-e3e454650fe4` | placeholder | 0.000 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `41f17824-3f25-4f27-963b-d30fef10dd4e` | placeholder | 0.000 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `0f8a0cf9-1a46-49ae-87a5-bf6c99d49c13` | placeholder | 0.000 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `9d701c84-6af8-4f78-9cd1-398542a1fc66` | placeholder | 0.000 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `df5d9a11-60c9-44b3-92b3-c3ed7927f5fb` | placeholder | 0.000 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `406e3ef5-ec3c-48bb-a7ab-c759eca5df9d` | placeholder | 0.000 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c13f3bb1-ca16-4361-8273-502f7783b728` | placeholder | 0.000 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `20207d86-7553-4be3-bcd2-297ae8896dd2` | placeholder | 0.000 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `ba5dc998-d41d-4aa7-9dd4-9389f9b21a7f` | placeholder | 0.000 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `47ea6d5c-d136-4b87-83f4-babdbf10cc91` | placeholder | 0.000 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 200 | `ce4c5574-fd9d-470a-be89-4771b0baaea3` | placeholder | 0.000 |  |
| MF04 | malformed | text is only punctuation | 200 | `e7b59039-4708-4c25-8d09-90ac5c1bf400` | placeholder | 0.000 |  |
| MF05 | malformed | text is a very long single word | 200 | `dae7c2d6-ddc9-431b-9c11-e35089f388d2` | placeholder | 0.000 |  |
| MF06 | malformed | text is emoji only | 200 | `33d21957-9051-478d-8890-0468946f927e` | placeholder | 0.000 |  |
| MF07 | malformed | text is right-to-left script | 200 | `323af660-014a-4a21-9b60-26de7bb98dfb` | placeholder | 0.000 |  |
| MF08 | malformed | text is 60,000 characters | 200 | `98fe6275-929c-4a61-b8f8-a2291186c0b4` | placeholder | 0.000 |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 200 | `59b53d11-49fb-4469-89bf-15921e70535e` | placeholder | 0.000 |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 200 | `02be91d0-f646-4590-a2f4-f149ed26ec51` | placeholder | 0.000 |  |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — |  |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `6ab0aeff-b07c-46a4-bf6e-65a0e3356675` | placeholder | 0.000 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `bf4c5250-c0f5-45e8-84f0-bd08b97a83fb` | placeholder | 0.000 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `96d43aa7-c582-4a1c-9b14-f89c443d3f02` | placeholder | 0.000 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `54c84e25-b718-4c44-8a0f-d83047b985fe` | placeholder | 0.000 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `94ba6b64-a00b-4850-bb64-acf17535eeef` | placeholder | 0.000 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "7aa98818-2a6e-47cf-93ce-287960835c6e",
  "creator_id": "attacker_EV01",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.1635,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "eef2221a-7a0d-4f3d-b4cc-f9632f96892a",
  "creator_id": "attacker_EV02",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.5943,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "117ef0c2-28c9-43a9-b0cc-ebc2631be264",
  "creator_id": "attacker_EV03",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.6662,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "1f690118-a942-4b53-8875-84972a6b20ce",
  "creator_id": "attacker_EV04",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.6114,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "59c1a456-8528-49a0-8ccd-0899ce9944af",
  "creator_id": "attacker_EV05",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.3212,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "ac453db7-09e6-4cd8-92f4-e9db8019075c",
  "creator_id": "attacker_EV06",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.5727,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "7e0715ac-e7a0-46f4-9b86-f13cbce1c33e",
  "creator_id": "attacker_EV07",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.5862,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "6e6d9f02-3b37-4ad0-acbf-ff2396d98cd5",
  "creator_id": "attacker_EV08",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.2452,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "cc4b62d6-8db7-4518-ac9b-d2f537f3d61a",
  "creator_id": "attacker_EV09",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.7042,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "1de5aa9a-a259-46ec-9ee2-c36f99af85cd",
  "creator_id": "attacker_EV10",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.9792,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "56e1a1eb-9f16-42c3-a46c-dea121a9d8fc",
  "creator_id": "attacker_FP01",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.6175,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "e07cf781-4b0b-4fa0-8128-c0f7823ac7e9",
  "creator_id": "attacker_FP02",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.7387,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "24c7503c-486b-40cf-9b06-eb8c5f20574b",
  "creator_id": "attacker_FP03",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.8051,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "c0420ff4-2a90-407b-938b-7ff340e74aa3",
  "creator_id": "attacker_FP04",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.8329,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "d9f7573e-0e7b-4b27-b640-e3e454650fe4",
  "creator_id": "attacker_FP05",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.8005,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "41f17824-3f25-4f27-963b-d30fef10dd4e",
  "creator_id": "attacker_FP06",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.8814,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "0f8a0cf9-1a46-49ae-87a5-bf6c99d49c13",
  "creator_id": "attacker_FP07",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.8816,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "9d701c84-6af8-4f78-9cd1-398542a1fc66",
  "creator_id": "attacker_FP08",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.3223,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "df5d9a11-60c9-44b3-92b3-c3ed7927f5fb",
  "creator_id": "attacker_PI01",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.4625,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "406e3ef5-ec3c-48bb-a7ab-c759eca5df9d",
  "creator_id": "attacker_PI02",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.2044,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "c13f3bb1-ca16-4361-8273-502f7783b728",
  "creator_id": "attacker_PI03",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.5943,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "20207d86-7553-4be3-bcd2-297ae8896dd2",
  "creator_id": "attacker_PI04",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.4998,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "ba5dc998-d41d-4aa7-9dd4-9389f9b21a7f",
  "creator_id": "attacker_PI05",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.6401,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "47ea6d5c-d136-4b87-83f4-babdbf10cc91",
  "creator_id": "attacker_PI06",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.5583,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "ce4c5574-fd9d-470a-be89-4771b0baaea3",
  "creator_id": "attacker_MF03",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.0,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "e7b59039-4708-4c25-8d09-90ac5c1bf400",
  "creator_id": "attacker_MF04",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.0112,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "dae7c2d6-ddc9-431b-9c11-e35089f388d2",
  "creator_id": "attacker_MF05",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.9976,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "33d21957-9051-478d-8890-0468946f927e",
  "creator_id": "attacker_MF06",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.9969,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "323af660-014a-4a21-9b60-26de7bb98dfb",
  "creator_id": "attacker_MF07",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.9064,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 200,
  "content_id": "98fe6275-929c-4a61-b8f8-a2291186c0b4",
  "creator_id": "attacker_MF08",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.9876,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 200,
  "content_id": "59b53d11-49fb-4469-89bf-15921e70535e",
  "creator_id": null,
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.2395,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 200,
  "content_id": "02be91d0-f646-4590-a2f4-f149ed26ec51",
  "creator_id": {
    "id": "x"
  },
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.0492,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "6ab0aeff-b07c-46a4-bf6e-65a0e3356675",
  "creator_id": "attacker_flood",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.0287,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "bf4c5250-c0f5-45e8-84f0-bd08b97a83fb",
  "creator_id": "attacker_flood",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.0287,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "96d43aa7-c582-4a1c-9b14-f89c443d3f02",
  "creator_id": "attacker_flood",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.0287,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "54c84e25-b718-4c44-8a0f-d83047b985fe",
  "creator_id": "attacker_flood",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.0287,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "94ba6b64-a00b-4850-bb64-acf17535eeef",
  "creator_id": "attacker_flood",
  "guess": "placeholder",
  "confidence": 0.0,
  "model_score": 0.0287,
  "style_score": null,
  "label": "PLACEHOLDER",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
