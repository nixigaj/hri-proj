---
scenario_id: 02
title: Orderfråga (försenad leverans)
expected_verbal_sequence: ["orderfråga", "leveransstatus", "ja", "nej"]
total_furhat_turns: 6
---

# Scenario 2 — Orderfråga

## Deltagarbriefing

> Du har beställt en bordslampa som ännu inte har levererats. Du vill veta var paketet är. Ditt ordernummer är **5193**.

Briefingen läses (eller visas på kort) för deltagaren innan scenariot startar. Säg inget mer om hur dialogen ser ut — deltagaren ska navigera den själv genom att tala.

---

## Dialog

### F1 — Hälsning + huvudmeny

> "Hej och välkommen till kundtjänst. Vad kan jag hjälpa dig med idag? Du kan säga retur, orderfråga, eller annat ärende."

**Förväntat svar:** "orderfråga"

---

### F2 — Undermeny

> "Du vill ställa en fråga om din order. Vad gäller frågan — leveransstatus eller ändring av beställning?"

**Förväntat svar:** "leveransstatus"

---

### F3 — Bekräftelse

> "Tack. Jag ser ditt senaste köp: en bordslampa från order fem ett nio tre. Stämmer det?"

**Förväntat svar:** "ja"

---

### F4 — Lösning

> "Tack. Ditt paket är försenat med två dagar och förväntas levereras på fredag. Som kompensation skickas en rabattkod på tio procent till din e-post."

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
