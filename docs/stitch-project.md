# Stitch — neplatný podklad mimo Davidův projekt

> **Mimo rozsah Davidova projektu:** David pracuje sám a Stitch není jeho projekt. Níže je uložený neplatný podklad; jeho formulace o týmu, spolupráci a předání nejsou aktuálním zadáním. Aktuální podklady jsou v [README](../README.md).

**Aktualizace:** 8. 10. 2026. Zdrojem produktového popisu je David; implementace zatím nebyla v tomto pracovním prostoru dostupná k ověření. Soutěžní požadavky jsou v [briefu](hackathon-brief.md).

## Rozhodnutí a stav

| Oblast | Aktuální informace |
| --- | --- |
| Název | Stitch |
| Směr | Agent automatizující Android a využívající zkušenosti z minulých úkolů |
| Popis mechanismu od týmu | Mapování interaktivních prvků a využití uložených zkušeností k orientaci v aplikaci |
| Aktuální aplikace | YouTube Music, podle Davida právě testovaná týmem |
| Implementace | Petr ji podle Davida commitnul do samostatného repozitáře. URL zatím nemáme; David čeká na přístup. |
| Toto repo | Týmová dokumentace; při kontrole GitHubu pouze větev main a původní dokumentace na commitu e70639d |
| Landing page | Vzniká; odkaz ani zdroj nejsou zde k dispozici. Vizuální styl ještě není finální. |
| Prezentace a video | Budoucí výstupy. Doporučeným základem videa je záznam skutečně fungujícího dema; případný krátký grafický úvod až podle času. |
| Ověření | Zde neproběhlo čtení implementace, spuštění agenta ani měření zlepšení. |

Výrok „mapuje všechny prvky“ zatím není ověřená úplnost. Zjistit, jaké prvky aplikace skutečně zpřístupňuje, co agent vidí a jak řeší chybějící nebo změněné prvky. Cílový uživatel a konkrétní opakovaná práce mimo demonstrační aplikaci zbývají upřesnit.

## Co získat při předání

1. URL repozitáře a přesnou větev/commit pro společnou práci.
2. Krátký společný průchod: jak se projekt spouští, jak se připojí zařízení a kudy se zadává úkol. Před instalací závislostí zkontrolovat instrukce a skripty.
3. Názvy potřebných proměnných prostředí a ukázkovou konfiguraci bez hodnot tajných údajů.
4. Jeden známý funkční úkol, jeho výchozí stav, očekávaný výsledek a známé potíže.
5. Umístění uložené mapy, historie, schopností a logů; způsob spuštění nové session se zachováním či oddělením paměti. Existující paměť před testy zachovat, testovat v samostatné kopii/profilu.
6. Přehled převzatých komponent a změn vzniklých během hackathonu. Předchozí zkušenost autora sama neříká, kolik kódu bylo převzato.

Po zpřístupnění nejprve vytvořit mapu skutečného toku programu s odkazy na soubory: zadání → pozorování UI → volba akce → provedení → ověření výsledku → uložení zkušenosti → načtení v další session. Toto je osnova pro čtení, ne tvrzení o současné architektuře.

## Navržená část práce pro Davida

Následující je návrh k dohodě s Petrem, nikoli již přidělená práce:

- Zprovoznit reprodukovatelný běh na druhém počítači a opravit chybějící návod či konfiguraci.
- Převzít ověřování učení: připravit scénáře, kontrolu výsledku a porovnání běhů.
- Podle dostupného rozhraní doplnit zobrazení důkazů: rozpoznané prvky, používaná schopnost, původ a výsledek testu. Data musí pocházet ze skutečného běhu.
- Z naměřeného chování připravit srozumitelné demo, landing copy a minutový pitch. Vzhled sladit až po potvrzení stylu.

Tím vzniká konkrétní technický výstup i podklad pro vysvětlení produktu. Rozsah integračního rozhraní je potřeba dohodnout nad kódem; nyní jej nevymýšlíme.

## Jak doložit učení

| Běh | Co má ukázat | Důkaz |
| --- | --- | --- |
| A: první úkol bez příslušné uložené zkušenosti | Jak agent objevuje postup a co po něm uloží | Výchozí registr/paměť, kroky, výsledek a změna uložených artefaktů |
| B: zopakovaný úkol z odpovídajícího výchozího stavu | Zda mu předchozí zkušenost skutečně pomáhá | Čas, modelová volání, chyby a ruční zásahy; ID využité zkušenosti |
| C: odlišný úkol v nové session | Přenos a kombinace dříve vytvořených schopností | Prázdný konverzační kontext, zachovaný deklarovaný registr, použitá ID/verze a ověřený výsledek |

Běh B je užitečná kontrola, ale nenahrazuje požadovaný běh C. Stejná obrazovka po předchozím úkolu může sama zrychlit druhý běh; proto zaznamenat a podle možnosti sjednotit stav aplikace. Samotný nižší čas nedokazuje příčinu. Pro silnější porovnání použít nový proces se zapnutou a vypnutou uloženou zkušeností při stejném výchozím stavu. Jednotlivé běhy označit jako ukázku, ne spolehlivý statistický benchmark.

Konkrétní úkoly v YouTube Music vybrat podle funkční implementace a dostupného účtu. Výsledek kontrolovat věcně, například zda vybraný interpret, album a skladba odpovídají zadání; samotné hlášení agenta „hotovo“ nestačí. Je-li úkolem přehrávání, definovat také důkaz stavu přehrávání. Konkrétní scénář a metriky zatím nejsou naměřené.

## Co ověřit vůči Frankensteinu

Mapa UI říká, kde se dá jednat. Historie říká, co se stalo. Opakovaně použitelná schopnost musí navíc mít rozhraní, deklarovaná oprávnění a spustitelné testy. Paměť nebo promptový postup mohou být součástí řešení; forma nemusí být jen nový zdrojový kód, ale musí splnit brief.

Z implementace zjistit, zda reálný úkol spouští tvorbu takové schopnosti, testy brání registraci vadné schopnosti a agent vytváří nebo rozšiřuje její vyhledávání a správu. Dále doložit skládání v nové session, izolaci generovaného kódu, stálá oprávnění a vynucené limity iterací a útraty. Aktuálně jsou tyto body **neověřené**, ne automaticky nesplněné.

## Doporučení pro odevzdávané video

Priorita je skutečný záznam produktu do 90 sekund. Pracovní rozvržení: 0–15 s problém a účel Stitche; 15–45 s první úkol, vznik schopností a testy; 45–75 s nová session a jiný úkol využívající předchozí schopnosti; 75–90 s doložený výsledek a limity. Čekání lze označeně zrychlit, selhání podle briefu nevystřihovat. Harmonogram záběrů přizpůsobit naměřené délce běhů.

Grafický úvod a společný vizuální styl mohou záznam doplnit, ale nejsou uzavřeným zadáním. Tvorba videa ani prezentace tímto dokumentem nezačíná. Samostatný Davidův projekt pro výrobu videí je mimo rozsah práce na Stitchi.
