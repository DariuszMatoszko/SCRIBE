# STANDARDY_CODEX (SCRIBE)

## 1) Zasady nadrzędne
- Nie psujemy działających funkcji. Zmieniamy tylko to, co potrzebne do celu patcha.
- Jeden patch = jeden cel = jeden test = jeden commit.
- Jeśli polecenie patcha i standardy są sprzeczne: standardy wygrywają.

## 2) Wyjątki od standardów
- Wyjątek jest dozwolony tylko, gdy instrukcja zawiera sekcję:
  WYJĄTEK OD STANDARDÓW:
  - <reguła>
  - <uzasadnienie>
- Bez tej sekcji: NIE łam standardów.

## 3) Zasady repo / plików
- Struktura `src/scribe_web/...` pozostaje.
- `ai_payload.json` jest jedynym plikiem „prawdy”, reszta to załączniki.
- Zapisy JSON robimy atomowo (tmp -> replace).

## 4) Zasady panelu (minimum)
- Panel ma wspierać: S, K, E, G, P, ||, ↩, Z.
- Status ma pokazywać SESJA / KROKI / PAUZA / AKCJA.
- K dodaje krok. E edytuje ostatni krok. G/P to jeszcze stub.

## 5) Zasady payload (AI_PAYLOAD v1)
- assets.screenshot i assets.annotated przechowują ścieżki względne (np. "steps/step_001.png").
- E nie tworzy nowego kroku — tylko uzupełnia assets.annotated w ostatnim kroku.
- K zawsze ustawia privacy.paused zgodnie ze stanem pauzy w momencie tworzenia kroku.

## 6) Protokół commitów
- Jeden patch = jeden commit.
- Message: stage04: <krótki opis>
