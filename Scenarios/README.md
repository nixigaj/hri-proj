# Scenarier — Kundtjänst med Furhat

Tre scenarier för HRI-studien om svenska dialekter i kundservice. Manus är identiska över de tre röstvillkoren (TTS / Rikssvenska / Skånska) — endast rösten varierar.

## Filer

| Fil | Scenario | Förväntad svarssekvens |
|-----|----------|------------------------|
| `01_retur.md` | Retur av skor | `retur → fel storlek → ja → nej` |
| `02_orderfraga.md` | Orderfråga (försenad lampa) | `orderfråga → leveransstatus → ja → nej` |
| `03_reklamation.md` | Reklamation (trasig vattenkokare) | `reklamation → defekt produkt → ja → nej` |

## Interaktionsmodell

Talad dialog. Furhat ställer en öppen fråga med 2–3 muntliga alternativ; deltagaren svarar verbalt. Studien körs som **Wizard-of-Oz**: en operatör lyssnar på deltagarens svar och avancerar dialogen via tangentbord (Enter = vidare, `r` = felsvar + repetera). Deltagaren har ingen tangentåtkomst.

Det finns en uppenbart korrekt väg genom varje scenario givet deltagarens briefing — alla deltagare följer samma flöde. Beslutet är inte testet; rösten är.

**Felsvar** vid otydligt/oväntat svar (samma rad återanvänds i alla scenarier, alla turer):

> *"Förlåt, jag uppfattade inte. Kan du upprepa?"* → Furhat upprepar aktuell meny.

## Manusstruktur

Varje scenario har **exakt 6 Furhat-turer**, identisk struktur:

| Tur | Funktion | Förväntar svar? |
|-----|----------|-----------------|
| F1 | Hälsning + huvudmeny (3 alternativ) | Ja |
| F2 | Undermeny (2 alternativ) | Ja |
| F3 | Bekräftelse av ärende (ja/nej) | Ja |
| F4 | Lösning meddelas | Nej |
| F5 | "Något mer?" (ja/nej) | Ja |
| F6 | Avslutning | Nej |

F1, F5 och F6 är ordagrant identiska över scenarier (endast huvudmenyns alternativ skiljer i F1). F6 är *exakt* samma mening i alla tre.

## Konventioner

- **Ordernummer uttalas siffra för siffra** (t.ex. `4827` → "fyra åtta två sju") — viktigt för konsistens mellan ElevenLabs-rösterna och TTS-baseline.
- **Inga scenariospecifika tonalitetskvirks.** Om något hörs som "skämtsamt" i ett scenario men "formellt" i ett annat — normalisera.

## Inspelnings-IDs

Varje rad har ett ID `F1`–`F6`. Ljudfiler genereras senare som:

```
audio/<scenario>/<röst>/F<n>.mp3
```

→ 6 turer × 3 scenarier × 3 röster = **54 ljudfiler**.

Felsvars-raden har egen ID `FX` och spelas in en gång per röst per scenario (ev. delas över scenarier eftersom raden är identisk).

## Cover story-påminnelse

Deltagarna får veta att de utvärderar *olika kundservice-scenarier*, inte olika röster. Manusen får inte avslöja röst-fokus. Scenarierna ska upplevas som tre olika ärenden, inte tre versioner av samma samtal.
