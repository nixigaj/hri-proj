---
scenario_id: 03
title: Reklamation av trasig vattenkokare
expected_key_sequence: [1, 1, 1, 2]
total_furhat_turns: 6
---

# Scenario 3 — Reklamation

## Deltagarbriefing

> Du har köpt en vattenkokare som slutade fungera efter en vecka. Du vill reklamera den och få en ny. Ditt ordernummer är **6471**.

Briefingen läses (eller visas på kort) för deltagaren innan scenariot startar. Säg inget mer om hur menyn ser ut — deltagaren ska navigera den själv.

---

## Dialog

### F1 — Hälsning + huvudmeny

> "Hej och välkommen till kundtjänst. Vad kan jag hjälpa dig med idag? Tryck 1 för reklamation, 2 för orderfråga, eller 3 för annat ärende."

**Förväntad tangent:** `1` (reklamation)

---

### F2 — Undermeny

> "Du vill göra en reklamation. Vad gäller reklamationen — defekt produkt eller fel artikel? Tryck 1 för defekt produkt, eller 2 för fel artikel."

**Förväntad tangent:** `1` (defekt produkt)

---

### F3 — Bekräftelse

> "Tack. Jag ser ditt senaste köp: en vattenkokare från order sex fyra sju ett. Stämmer det? Tryck 1 för ja, eller 2 för nej."

**Förväntad tangent:** `1` (ja)

---

### F4 — Lösning

> "Tack. Jag skickar nu en ny vattenkokare till dig samt en hämtetikett för den defekta produkten. Allt skickas till din e-post."

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
