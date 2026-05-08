---
scenario_id: 01
title: Retur av skor
expected_verbal_sequence: ["retur", "fel storlek", "ja", "nej"]
total_furhat_turns: 6
---

# Scenario 1 — Retur

## Deltagarbriefing

> Du har beställt ett par skor online som inte passade. Du vill returnera dem och få pengarna tillbaka. Ditt ordernummer är **4827**.

Briefingen läses (eller visas på kort) för deltagaren innan scenariot startar. Säg inget mer om hur dialogen ser ut — deltagaren ska navigera den själv genom att tala.

---

## Dialog

### F1 — Hälsning + huvudmeny

> "Hej och välkommen till kundtjänst. Vad kan jag hjälpa dig med idag? Du kan säga retur, orderfråga, eller annat ärende."

**Förväntat svar:** "retur"

---

### F2 — Undermeny

> "Du vill göra en retur. Vad gäller returen — fel storlek eller fel produkt?"

**Förväntat svar:** "fel storlek"

---

### F3 — Bekräftelse

> "Tack. Jag ser ditt senaste köp: ett par skor från order fyra åtta två sju. Stämmer det?"

**Förväntat svar:** "ja"

---

### F4 — Lösning

> "Tack. Jag skickar nu en returetikett till din e-post. Skorna ska returneras inom fjorton dagar och pengarna återbetalas inom fem bankdagar."

*Inget svar från deltagaren. Furhat fortsätter direkt till F5 efter kort paus.*

---

### F5 — Något mer?

> "Är det något mer jag kan hjälpa dig med?"

**Förväntat svar:** "nej"

---

### F6 — Avslutning

> "Tack för att du kontaktade oss. Ha en bra dag."

*Scenariot slut.*

---

## Felsvar (FX)

Om deltagaren ger ett otydligt eller oväntat svar på F1, F2, F3 eller F5:

> "Förlåt, jag uppfattade inte. Kan du upprepa?"

→ Furhat upprepar aktuell meny.
