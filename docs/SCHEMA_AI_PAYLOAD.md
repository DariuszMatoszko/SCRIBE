# Schema AI Payload (v1)

Ten format jest przygotowany **dla AI**, a nie dla człowieka. Struktura ma być stabilna i łatwa do parsowania.

## Główne pola

- `session_meta`
  - `project_name`: nazwa projektu.
  - `created_at`: ISO8601 z tz Europe/Warsaw.
  - `purpose`: stała wartość `automation_for_ai`.
  - `env`: metadane środowiska (`os`, `python`, `language`).

- `steps`
  - Lista kroków sesji (obiekty v1).

- `raw_logs`
  - Miejsce na surowe logi (obecnie puste).

## Krok (v1)

Każdy krok zawiera:

- `id`, `ts`, `url`, `title`
- `assets`
  - `screenshot`, `annotated`
- `text`
  - `voice_transcript_raw`
  - `voice_transcript_clean`
  - `notes_clean`
- `between_steps_summary`
  - `clicks`, `keys_summary`, `navigations`
- `probe`
  - `clicked_element`, `network_summary`
- `privacy`
  - `paused`, `redactions_applied`
