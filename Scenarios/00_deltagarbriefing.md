---
title: Deltagarbriefing — läses högt innan testning
language: sv
estimated_duration_min: 3
---

# Deltagarbriefing

Läses ordagrant (eller näst intill) av försöksledaren **innan** scenarierna börjar. Cover story-rad är obligatorisk — får inte avslöja att studien handlar om röst/dialekt.

---

## 1. Välkomst (30 s)

> "Hej och välkommen. Tack för att du ställer upp i den här studien. Jag heter [NAMN] och jag kommer att leda testningen idag. Det tar cirka [N] minuter totalt."

---

## 2. Vad studien handlar om — *cover story* (30 s)

> "Vi undersöker hur människor upplever **olika kundservice-scenarier** med en robotassistent. Du kommer att få prata med en robot, Furhat, som agerar kundtjänst i tre olika ärenden. Vi vill veta hur du upplever interaktionen."

**Får inte sägas**: att röst eller dialekt är det som varieras. Om deltagaren frågar direkt — säg:
> "Det berättar jag mer om i debriefingen efteråt."

---

## 3. Hur interaktionen går till (60 s)

> "Du kommer att sitta framför roboten och **prata med den som du skulle prata med en vanlig kundtjänst**. Inga knappar, ingen skärm — bara rösten. Du svarar muntligt på det roboten frågar."
>
> "Roboten ställer en fråga, du svarar, så fortsätter samtalet. Om du säger något den inte förstår, säger den 'Förlåt, jag uppfattade inte. Kan du upprepa?' och frågar igen."
>
> "Tala i normal samtalsvolym. Vänta tills roboten har talat klart innan du svarar — annars kan den missa vad du säger."

---

## 4. Scenarierna (60 s)

> "Du kommer att gå igenom **tre scenarier**. Inför varje scenario får du ett kort med en kort beskrivning av ditt ärende — t.ex. att du vill returnera en produkt eller fråga om en försenad leverans. Läs kortet, känn dig in i situationen, och säg till när du är redo att starta."
>
> "Det finns ingen 'rätt' eller 'fel' — beslutet du fattar är inte det vi mäter. Bara gör som du naturligt skulle göra med beskrivningen du har fått."
>
> "Mellan scenarierna får du svara på några korta frågor om hur du upplevde samtalet."

---

## 5. Inspelning + samtycke (30 s)

> "Samtalen spelas in [ljud / video / både och — välj] för analys. Materialet behandlas anonymt och bara forskargruppen ser det. Du kan när som helst avbryta utan att ange skäl, och be om att din data raderas i efterhand."
>
> "Har du läst och skrivit under samtyckesformuläret?" → *kontrollera*

---

## 6. Sista frågor (30 s)

> "Har du några frågor innan vi börjar?"

*Svara på frågor men avslöja inte cover story.*

---

## 7. Starta

> "Då kör vi. Här är kortet för första scenariot — läs igenom det, och säg till när du är klar."

→ Räck över **scenariokort 1**. Vänta på "klar"/nick. Starta `skill.py --scenario 1 --voice <X>`.

---

## Mellan scenarier

> "Bra. Då går vi vidare. Här är några korta frågor om samtalet du just hade." → *enkät*
>
> *(efter enkät)* "Här är nästa scenario." → *räck över kort 2/3*

---

## Efter sista scenariot — debriefing

> "Det var sista scenariot. Tack. Nu ska jag berätta vad studien egentligen handlar om: vi varierade **rösten** roboten använde — du fick höra tre olika röster (TTS-baseline, Rikssvenska, Skånska) en i varje scenario. Det vi mäter är om röstens karaktär påverkar hur du upplever interaktionen."
>
> "Märkte du av det? Vad tänkte du?"

→ Fri diskussion. Spara fältnoteringar.

> "Tack så mycket för din tid. Här är din [ersättning / godis / inget]."

---

## Försöksledarens checklista — innan deltagaren kommer in

- [ ] Furhat Launcher igång, virtuell robot startad
- [ ] Voice tilldelad (kolla `get_voices()` returnerar något)
- [ ] `skill.py` testkört en gång för aktuell `--voice` + `--scenario`
- [ ] Ljudserver når Furhat (`curl http://<audio-host>:8000/` från Furhat-sidan)
- [ ] Brusnivå rimlig i rummet
- [ ] Samtyckesformulär utskrivet
- [ ] Scenariokort 1/2/3 utskrivna och i ordning enligt counterbalanceringsschemat
- [ ] Inspelning startad (om används)
- [ ] Penna + enkätark redo
