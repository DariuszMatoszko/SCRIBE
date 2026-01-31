# STANDARDY_CODEX (SCRIBE)

## 1) Zasady nadrzędne
- Nie psujemy działających funkcji. Zmieniamy tylko to, co potrzebne do celu patcha.
- Jeden patch = jeden cel = jeden test = jeden commit.
- Jeśli instrukcja patcha i standardy są sprzeczne: standardy wygrywają.

## 2) Wyjątki od standardów
- Wyjątek jest dozwolony tylko, gdy instrukcja zawiera sekcję:
  WYJĄTEK OD STANDARDÓW:
  - <reguła>
  - <uzasadnienie>
- Bez tej sekcji: NIE łam standardów.

## 3) Protokół: kiedy użyć „Research/Pro”
- Jeśli pojawia się problem zależny od platformy (macOS/Tk/Python path) i brak jednoznacznej diagnozy:
  przerwij implementację i poproś o analizę w trybie badawczym Pro.
- Jeśli diagnoza jest jasna (jak błąd w logu), implementuj bez Pro.

## 4) Zasady panelu UI (minimalne i twarde)
- Panel ma być ultrakompaktowy:
  - minimalne marginesy, odstępy między przyciskami 1–2 px
  - status mały (nie może wymuszać dużej ramki)
  - brak obwódek przycisków
- START nazwy projektu: bez okna z przyciskami, tylko mały pasek z Entry:
  - pojawia się NAD panelem
  - ENTER = zatwierdź, ESC = anuluj
- K: tworzy krok + screenshot (assets.screenshot)
- E: edytuje ostatni screenshot „mazakiem” i zapisuje assets.annotated
- G: działa w trybie toggle START/STOP, dopina audio/transkrypcję do ostatniego kroku (lub kroku z momentu START, jeśli w trakcie powstał nowy). Pliki zapisywane do transcripts/step_XXX.(wav/_raw.txt/_clean.txt). Brak zależności audio/whisper nie może wywalać panelu — błąd ma być obsłużony lokalnie w G. (Aktualizacja: wymagane w patchu BTN G.)
- P zostaje stubem na później

## 5) Zasady payload (AI_PAYLOAD v1)
- assets.screenshot / assets.annotated to ścieżki względne w obrębie folderu sesji (np. "steps/step_001.png")
- E nie tworzy nowego kroku — tylko uzupełnia assets.annotated w ostatnim kroku
- Zapisy JSON atomowo
