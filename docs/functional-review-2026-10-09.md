# Funkční review pracovního agenta

Novější kontrola: [audit všech Frankenstein požadavků a posouzení pivotů, přibližně 04:23](frankenstein-requirements-audit-2026-10-09.md). Obsahuje i procházející regresní testy následných oprav; níže zůstává původní stav a reprodukce z doby tohoto review.

**Verdikt: základ učení a oprav funguje, ale aplikace jako celek ještě není spolehlivě dokončená.** Nezávislá kontrola reprodukovala vymyšlený výsledek v navazujícím chatu, ztrátu projektu mezi záložkami, překročení povoleného síťového originu a falešné potvrzení browser výsledku. Nový browser úkol nedokončil tvorbu postupu ani po vyčerpání povolených volání. Tyto problémy mají přednost před přidáváním dalších funkcí.

Kontrola proběhla 9. 10. 2026 přibližně 03:49–04:05 Europe/Prague. Výchozí byl dokončený checkpoint MAIN. Během kontroly MAIN znovu začal doplňovat spotřebu a cenu; tato souběžná změna není předstíraná jako součást původního modelového průchodu. Relevantní příčiny níže byly znovu nalezeny i v aktuálním zdroji. Poslední commit při zahájení byl `be1328d`; funkční rozšíření jsou stále v pracovním stromu.

## Rozsah a důkazy

Reviewer spustil samostatnou instanci na portu 8781 s prázdnou databází, existujícím potvrzeným Free nastavením Gemini a výhradně syntetickými daty. Zadávání úkolů, příloh, oprav, aktivace verzí a ukládání workflow proběhlo přes skutečné UI. Hlavní instance na portu 8767 a její registr nebyly těmito kontrolami změněné.

- Výchozí sada: **22 testů prošlo**, 15,323 sekundy.
- Po souběžném přidání účtování: **30 testů prošlo**, 32,522 sekundy. [Úplný výstup](review-evidence-2026-10-09/functional/infra-tests-current.txt).
- Osm skutečných modelových běhů včetně záměrného zastavení a negativních kontrol. Jeden běh označený `completed` vrátil vymyšlená data; počet dokončených běhů není počet správných výsledků.
- [Výsledky a události živých běhů](review-evidence-2026-10-09/functional/results.json), [sondy kontroly počtu a přesměrování](review-evidence-2026-10-09/functional/boundary_probes.py), [otisky zdrojů při zahájení](review-evidence-2026-10-09/functional/source-hashes-at-start.json).
- Starší reprodukční sondy byly znovu spuštěné: přenos mapy mezi projekty, nesrovnatelné otisky registru a přijetí modelového `finish` bez browser akce stále reprodukovaly problém.

Pro spuštění nových sond z kořene repozitáře: `PYTHONPATH=. .venv/bin/python docs/review-evidence-2026-10-09/functional/boundary_probes.py`. Používají dva lokální HTTP servery a existující Chrome konektor. Jejich výstup popisuje pozorované chování; úspěšný exit neznamená, že hranice byla dodržena.

## Stav funkcí

| Funkce | Nezávisle ověřený stav |
| --- | --- |
| Projekt a instrukce | Projekt se vytvořil a přežil reload. Instrukce se dostala do reálného modelového výsledku. Souběžné ukládání ze dvou záložek ztrácí změny. |
| CSV příloha a výsledek | Tři řádky se správně změnily na dva jedinečné kontakty a jednu duplicitu. Příloha i výsledek byly viditelné v UI. |
| Chyba a Try again | První pokus skončil neplatným JSON od modelu. UI chybu ukázalo, Try again obnovilo zadání i přílohu a opakování uspělo. |
| Vytvoření schopnosti | Z čistého registru vznikla `Process Contacts CSV`, prošla třemi testy a byla použita. |
| Oprava z UI | Explicitní případ se dvěma lidmi bez emailu odhalil chybu v1. Dva kandidáty prošly původními i novým testem, vznikla v2 se čtyřmi testy. |
| Knihovna a verze | Detail, původ, testy, výběr verze, deaktivace, aktivace v1 a návrat na v2 skutečně fungovaly. |
| Export | Stažený výsledek i export v2 obsahovaly správný JSON; soubory byly přečtené a porovnané. Událost stažení v automatizačním rozhraní měla timeout, skutečný soubor se ale stáhl. |
| Uložené workflow | Uložení, zobrazení po reloadu a použití s novým CSV prošlo. Běh použil v2 bez nové instalace, zachoval oba lidi bez emailu a správně oddělil další duplicitu; dvě modelová volání. |
| Vyhledávání | Vyhledání konkrétního skillu v UI fungovalo. To není agentem vytvořené discovery. |
| Běžné pokračování chatu | Selhalo: předchozí výsledek se automaticky nepředal a model vymyslel jiné osoby. Stejné zadání přes Follow up uspělo. |
| Computer | Připojení practice app, mapa pěti prvků, náhled, předání úkolu a odpojení fungovaly. Základní klikání/vyplňování navíc prošlo automatickým testem ve skutečném Chrome. |
| Nový generovaný browser postup | Můj nový úkol se dvěma účastníky selhal po 12 voláních, bez přijaté schopnosti. Předchozí úspěšné demonstrace MAIN tím nezmizely, ale nedokládají spolehlivost nového zadání. |
| Stop | Zrušení přes UI skončilo stavem `cancelled`, po doběhnutí aktuální modelové operace. Další krok se neprovedl. |
| Schválení externí akce | Infrastrukturní test čekání a zrušení prošel. Skutečný externí účet nebyl použit. Síťová izolace má samostatnou chybu popsanou níže. |
| Spotřeba a cena | Osm nových automatických testů prošlo jako součást sady 30. Nové obrazovky a skutečné vykázání ceny nebyly součástí tohoto samostatného UI průchodu. |

## P1 Navazující chat vymýšlí data a hlásí úspěch

Po zpracování nového CSV předchozí výsledek obsahoval kontakty `Missing One`, `Missing Two`, `Evan`. Běžná další zpráva „From the contacts in your previous result, list only the names in reverse order“ dostala pouze vstup `{"files":[]}`. Výsledek byl `Charlie Brown`, `Bob Jones`, `Alice Smith`, přesto se zobrazil jako dokončený a zkontrolovaný. Model při tom vytvořil další skill a vykonal jej nad vymyšlenými vstupy.

Příčina je v `web/app.js`, funkci `submit` kolem řádku 90: `previous_result` se připojuje pouze po tlačítku Follow up. `workbench/engine.py`, funkce `task`, záměrně pokaždé vytváří prázdnou historii. `finish` přijímá tvrzení modelu bez další kontroly původu výsledku.

Kontrolní opakování stejného textu přes Follow up připojilo správná data a vrátilo `Evan`, `Missing Two`, `Missing One`. Opravit automatické pokračování stejného chatu a při chybějících podkladech vracet požadavek na doplnění, nikoli úspěch. Novou nezávislou session pro soutěžní důkaz dál explicitně oddělovat.

## P1 Uložení z druhé záložky smaže novější projekt

Dvě záložky načetly stejné workspace. V první vznikl projekt `QA tab A must survive`, ve druhé `QA tab B`. Po uložení druhé záložky a reloadu první existoval jen projekt B a původní kontrolní projekt. A zmizel bez upozornění.

`web/app.js`, `persist`, posílá celý lokální objekt. `workbench/store.py:109`, `save_workspace`, jej bez verze nebo sloučení kompletně nahrazuje. Obnova UI načítá běhy, ale nesynchronizuje celý workspace mezi záložkami.

Použít změny jednotlivých záznamů nebo kontrolu verze při zápisu se zpracováním konfliktu. Přidat test dvou klientů, který musí zachovat oba nově vytvořené projekty a související instrukce/workflows.

## P1 Přesměrování překročí povolený origin

Lokální povolená stránka načetla obrázek přes vlastní URL, která vrátila HTTP 302 na druhý lokální server s jiným portem. Druhý server skutečně obdržel požadavek `/cross-origin-probe`. Nešlo o externí účet ani přenos soukromých dat.

`workbench/browser/driver.cjs:39` kontroluje origin zachyceného požadavku, ale následné `route.continue()` v této cestě nezabránilo přesměrovanému požadavku. Tvrzení „Only this site is allowed“ proto přesahuje skutečně vynucenou hranici.

Kontrolovat každý cíl přesměrování před jeho odesláním, případně nepovolená přesměrování blokovat na síťové vrstvě. Regresní test musí hlídat počet požadavků na druhém serveru, ne pouze URL výsledné stránky.

## P1 Kontrola výsledku může potvrdit chybný počet i neprovedený úkol

`workbench/browser_control.py:128` používá hledání podřetězce. Kontrolní stav `11 registered` prošel očekáváním `1 registered`. Sonda simulovala stav konektoru; netvrdí, že model sám tuto chybu vyvolal v živém registračním běhu.

Navíc modelový `finish` ve `workbench/engine.py` není navázaný na povinné ověření browser úkolu. Starší sonda i po dokončení checkpointu získala `completed` bez jediné browser akce. `run_plan` tedy má lokální kontrolu, ale není univerzální bránou dokončení.

Pro demo použít přesně vyhodnocené podmínky výsledku: počet jako číslo a konkrétní záznam se správnými poli. U úkolu, který vyžaduje změnu aplikace, odmítnout dokončení bez příslušného důkazu. Ověřovat i workshop a stav účastníka, nejen výskyt jména kdekoli na stránce.

## P2 Nový browser postup se může zaseknout na nejednoznačných očekáváních testů

Nový úkol pro QA Robin a QA Jules třikrát zkusil vytvoření a opravu plánu a vyčerpal limit 12 volání. Část kandidátů byla skutečně chybná, například měla neplatnou hodnotu checkboxu. U posledních kandidátů ale selhával jediný test kvůli jinému počtu prvků `expected_text`; opravný kandidát přidával další kontrolu výsledku oproti přesnému JSON očekávanému autorem testu.

`workbench/engine.py:203` požaduje přesnou rovnost celého plánu. Kontrakt přitom jednoznačně neurčuje jedinou přípustnou posloupnost ani jediný seznam ověření. Ani odlišný plán automaticky není správný; podstatné je, že test nyní nerozlišuje ekvivalentní variantu od chybného chování.

Stanovit kanonický výstup plánu nebo testovat sémantické podmínky akcí a výsledku. Zachovat povinné kontroly oprávnění, vstupů a výsledného stavu. Další opakování generování bez úpravy této hranice není důkaz opravy.

## Další potvrzené problémy

- **P2 Mapy aplikací se sdílejí mezi projekty.** `Store.remember_app` ukládá pouze podle originu; `ScopedStore` aplikace nefiltruje. Mapa projektu A je dostupná v B. Rozsah musí být explicitní.
- **P2 Otisky registru porovnávají různý rozsah.** `Application.start` zapisuje globální `registry_before`, scoped Engine pak lokální `registry_after`. Běh bez změny schopností může hlásit jiný hash. Před/po počítat nad stejnou množinou a uložit její scope.

## Co chybí v produktu a v soutěžním průchodu

Agentem vytvořené discovery a správa ani jiný úkol v čisté session kombinující více vzniklých schopností stále nemají kompletní důkaz. Můj úspěšný reuse jedné opravené schopnosti toto nenahrazuje. Vyhledávání v UI a ručně napsaný registr se do tohoto požadavku nepočítají.

Plánované rutiny, obecná delegace specialistům, učení pozorováním člověka, nativní desktop/Android, týmové sdílení a agentem prováděný upload/download nejsou implementované. Textová příloha do chatu je jiná funkce než upload souboru agentem do cílové aplikace. Mobilní verze, kompletní přístupnost a reálné externí účty nebyly tímto review ověřené.

Pořadí oprav: pokračování chatu a ochrana workspace před ztrátou změn; skutečná síťová hranice a pravdivé dokončení; stabilní testování browser plánů; projektová paměť a otisky registru. Poté zopakovat tyto konkrétní případy, zaznamenat celý Frankenstein průchod a commitnout/pushnout ověřenou implementaci. Vlastní přínos přes testované opravy je doložený; spolehlivost celého produktu a převaha nad Hermesem doložené nejsou.

Reviewer změnil pouze review dokumentaci a testovací důkazy. Neprovedl opravy implementace, úpravy pravidel, push ani odevzdání projektu.
