---
scenario_id: 02
title: Orderfråga (försenad leverans)
expected_key_sequence: [2, 1, 1, 2]
total_furhat_turns: 6
---

# Scenario 2 — Orderfråga

## Deltagarbriefing

> Du har beställt en bordslampa som ännu inte har levererats. Du vill veta var paketet är. Ditt ordernummer är **5193**.

Briefingen läses (eller visas på kort) för deltagaren innan scenariot startar. Säg inget mer om hur menyn ser ut — deltagaren ska navigera den själv.

---

## Dialog

### F1 — Hälsning + huvudmeny

> "Hej och välkommen till kundtjänst. Vad kan jag hjälpa dig med idag? Tryck 1 för retur, 2 för orderfråga, eller 3 för annat ärende."

**Förväntad tangent:** `2` (orderfråga)

---

### F2 — Undermeny

> "Du vill ställa en fråga om din order. Vad gäller frågan — leveransstatus eller ändring av beställning? Tryck 1 för leveransstatus, eller 2 för ändring."

**Förväntad tangent:** `1` (leveransstatus)

---

### F3 — Bekräftelse

> "Tack. Jag ser ditt senaste köp: en bordslampa från order fem ett nio tre. Stämmer det? Tryck 1 för ja, eller 2 för nej."

**Förväntad tangent:** `1` (ja)

---

### F4 — Lösning

> "Tack. Ditt paket är försenat med två dagar och förväntas levereras på fredag. Som kompensation skickas en rabattkod på tio procent till din e-post."

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
