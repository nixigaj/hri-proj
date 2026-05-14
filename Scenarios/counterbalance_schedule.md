---
title: Counterbalanceringsschema — 9 deltagare
design: Latin 3×3 på röst (scenariordning fix), replikerat 3×
---

# Counterbalanceringsschema (n = 9)

Scenarier körs alltid i ordning **S1 → S2 → S3**. Endast **rösten** roteras.

Latin 3×3 på röst:

- varje röst förekommer en gång i varje position (1:a/2:a/3:e scenariot)
- varje röst×scenario-par förekommer exakt en gång per block om 3 deltagare (alla 9 par täckta)

Replikera blocket 3 gånger → n = 9.

## Förkortningar

| Kod | Röst | Kod | Scenario |
|-----|------|-----|----------|
| T | TTS-baseline | S1 | Retur |
| R | Rikssvenska | S2 | Orderfråga |
| K | Skånska | S3 | Reklamation |

## Schema

| Deltagare | S1 (Retur) | S2 (Orderfråga) | S3 (Reklamation) |
|-----------|------------|-----------------|------------------|
| P1 | T | R | K |
| P2 | R | K | T |
| P3 | K | T | R |
| P4 | T | R | K |
| P5 | R | K | T |
| P6 | K | T | R |
| P7 | T | R | K |
| P8 | R | K | T |
| P9 | K | T | R |

## Balanskontroll

**Röst per position** (n = 9):

| Position | T | R | K |
|----------|---|---|---|
| S1 | 3 | 3 | 3 |
| S2 | 3 | 3 | 3 |
| S3 | 3 | 3 | 3 |

**Röst×scenario-par** (n = 9): varje av 9 par körs 1 gång (3 par per block × 3 block).

## Körkommandon per deltagare

```
# P1, P4, P7  — ordning T R K
.venv/bin/python skill.py --scenario 1 --voice tts          --furhat-host <HOST>
.venv/bin/python skill.py --scenario 2 --voice rikssvenska  --furhat-host <HOST>
.venv/bin/python skill.py --scenario 3 --voice skanska      --furhat-host <HOST>

# P2, P5, P8  — ordning R K T
.venv/bin/python skill.py --scenario 1 --voice rikssvenska  --furhat-host <HOST>
.venv/bin/python skill.py --scenario 2 --voice skanska      --furhat-host <HOST>
.venv/bin/python skill.py --scenario 3 --voice tts          --furhat-host <HOST>

# P3, P6, P9  — ordning K T R
.venv/bin/python skill.py --scenario 1 --voice skanska      --furhat-host <HOST>
.venv/bin/python skill.py --scenario 2 --voice tts          --furhat-host <HOST>
.venv/bin/python skill.py --scenario 3 --voice rikssvenska  --furhat-host <HOST>
```

## Anteckningar

- Tilldela deltagar-ID i ankomstordning (P1, P2, …). Sortera **inte** efter demografi — bryter balansen.
- Vid avhopp mitt i: notera position, kassera data, kör nästa deltagare på samma rad-ID.
- Utöka i steg om 3 (P10–P12 = samma som P1–P3). Aldrig 1–2 extra — bryter balansen.
- Pilotdeltagare räknas inte; kör valfri ordning.
- Scenarioordning fix → ordningseffekter på scenario kan **inte** separeras från scenarioinnehåll. Acceptabelt om huvudfrågan är röstens effekt, inte scenariots.
