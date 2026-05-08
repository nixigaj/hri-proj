---
scenario_id: 03
title: Reklamation av trasig vattenkokare
expected_verbal_sequence: ["reklamation", "defekt produkt", "ja", "nej"]
total_furhat_turns: 6
---

# Scenario 3 — Reklamation

## Deltagarbriefing

> Du har köpt en vattenkokare som slutade fungera efter en vecka. Du vill reklamera den och få en ny. Ditt ordernummer är **6471**.

Briefingen läses (eller visas på kort) för deltagaren innan scenariot startar. Säg inget mer om hur dialogen ser ut — deltagaren ska navigera den själv genom att tala.

---

## Dialog

### F1 — Hälsning + huvudmeny

> "Hej och välkommen till kundtjänst. Vad kan jag hjälpa dig med idag? Du kan säga reklamation, orderfråga, eller annat ärende."

**Förväntat svar:** "reklamation"

---

### F2 — Undermeny

> "Du vill göra en reklamation. Vad gäller reklamationen — defekt produkt eller fel artikel?"

**Förväntat svar:** "defekt produkt"

---

### F3 — Bekräftelse

> "Tack. Jag ser ditt senaste köp: en vattenkokare från order sex fyra sju ett. Stämmer det?"

**Förväntat svar:** "ja"

---

### F4 — Lösning

> "Tack. Jag skickar nu en ny vattenkokare till dig samt en hämtetikett för den defekta produkten. Allt skickas till din e-post."

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
