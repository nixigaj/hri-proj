---
scenario_id: 01
title: Retur av skor
expected_key_sequence: [1, 1, 1, 2]
total_furhat_turns: 6
---

# Scenario 1 — Retur

## Deltagarbriefing

> Du har beställt ett par skor online som inte passade. Du vill returnera dem och få pengarna tillbaka. Ditt ordernummer är **4827**.

Briefingen läses (eller visas på kort) för deltagaren innan scenariot startar. Säg inget mer om hur menyn ser ut — deltagaren ska navigera den själv.

---

## Dialog

### F1 — Hälsning + huvudmeny

> "Hej och välkommen till kundtjänst. Vad kan jag hjälpa dig med idag? Tryck 1 för retur, 2 för orderfråga, eller 3 för annat ärende."

**Förväntad tangent:** `1` (retur)

---

### F2 — Undermeny

> "Du vill göra en retur. Vad gäller returen — fel storlek eller fel produkt? Tryck 1 för fel storlek, eller 2 för fel produkt."

**Förväntad tangent:** `1` (fel storlek)

---

### F3 — Bekräftelse

> "Tack. Jag ser ditt senaste köp: ett par skor från order fyra åtta två sju. Stämmer det? Tryck 1 för ja, eller 2 för nej."

**Förväntad tangent:** `1` (ja)

---

### F4 — Lösning

> "Tack. Jag skickar nu en returetikett till din e-post. Skorna ska returneras inom fjorton dagar och pengarna återbetalas inom fem bankdagar."

*Ingen tangenttryckning. Furhat fortsätter direkt till F5 efter kort paus.*

---

### F5 — Något mer?

> "Är det något mer jag kan hjälpa dig med? Tryck 1 för ja, eller 2 för nej."

**Förväntad tangent:** `2` (nej)

---

### F6 — Avslutning

> "Tack för att du kontaktade oss. Ha en bra dag."

*Scenariot slut.*

---

## Felsvar (FX)

Om deltagaren trycker en otillåten/oväntad tangent på F1, F2, F3 eller F5:

> "Förlåt, jag uppfattade inte. Var god försök igen."

→ Furhat upprepar aktuell meny.
