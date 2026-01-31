# VOICE_STAGE05 — nagrywanie + transkrypcja (Whisper, PL)

## Instalacja zależności

```bash
python3 -m pip install -r requirements.txt
```

## Voice demo (CLI)

```bash
python3 -m scribe_web --voice-demo
```

Flow:
1. Podaj nazwę projektu.
2. Powstanie sesja i jeden krok stub.
3. Nagrywanie audio (~10 s), transkrypcja Whisper PL.
4. Konsola poprosi o ewentualną korektę "clean".

## Gdzie trafiają pliki

W katalogu sesji, w `transcripts/`:
- `step_XXX.wav`
- `step_XXX_raw.txt`
- `step_XXX_clean.txt`

W `ai_payload.json` (ostatni krok):
- `text.voice_transcript_raw` i `text.voice_transcript_clean` zawierają ścieżki względne.
