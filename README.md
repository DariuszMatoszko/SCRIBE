# SCRIBE_WEB

SCRIBE_WEB to webowy rejestrator działań dla AI. Ten etap zawiera jedynie szkielet projektu oraz minimalny smoke test.

## Smoke test

Uruchom:

```bash
python -m scribe_web --smoke
```

Wyniki zapisują się w:
- `sessions/_smoke_test/ai_payload.json`
- `logs/scribe_web.log`

## Instalacja zależności

```bash
python3 -m pip install -r requirements.txt
```

## Demo

Uruchom:

```bash
python3 -m scribe_web --demo
```

## Panel 2×4

Uruchom:

```bash
python3 -m scribe_web --panel
```

## Flow Etapu 4

S -> K (screenshot) -> E (annot) -> Z

## Uruchamianie bez Terminala (macOS)

- Dwuklik: `tools/macos/RUN_PANEL.command`
- Instalacja .app: `tools/macos/INSTALL_PANEL_APP.command` (dwuklik), potem Launchpad
