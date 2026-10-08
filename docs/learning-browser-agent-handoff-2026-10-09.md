# Pracovní návrh agenta učícího se práci v aplikacích

**Stav k 9. 10. 2026 přibližně 00:17 Europe/Prague.** Podklad pro Davida a dalšího agenta k rychlému rozhodnutí o nočním prototypu. Davidovi se líbí agent, který plní uživatelské úkoly v aplikacích a z vlastní práce získává opakovaně použitelné schopnosti. Konkrétní demo, název a stack ještě nepotvrdil. Tento dokument není tvrzením o funkční implementaci ani pokynem začít libovolný produkt.

**Doporučení asistenta:** jeden agent, jeden prohlížeč a malá knihovna schopností, které agent vytvoří za běhu, otestuje a použije v další session. Lidská ukázka je případná pomoc, nikoli povinný začátek. Přínos ověřovat proti stejnému agentovi bez naučených schopností. Dnes nerozšiřovat rešerši o další obecné frameworky.

## Co David skutečně chce

Uživatel napíše požadovaný výsledek. Agent se zorientuje v aplikaci, dokončí práci a uchová si ověřený postup. Příště u podobné práce s jinými vstupy nemusí znovu objevovat celou cestu. Uživatel má vidět skutečné akce, výsledek a to, co se agent naučil; může upřesnit styl, opravit nepochopení a zkontrolovat naučené schopnosti.

Nejnovější příklad: „Go on YouTube, upload this video, make the title and description in this style.“ David zvažuje, že si agent styl i postup uchová a další práci na YouTube provede efektivněji. YouTube je kandidát na demo, nikoli potvrzená integrace nebo souhlas s publikováním videí. Bakaláři, docházka a telefonní budík byly rovněž ilustrace.

David nechce automatický souhlas ani další seznam buzzwords. Chce užitečný, srozumitelný produkt, dobrý uživatelský zážitek a přesvědčivou ukázku. „Plain“ se nemá řešit přidáním zbytečných funkcí: důležitý je pozorovatelný přenos zkušenosti na další práci.

David na projektu Frankenstein pracuje sám. Stitch není jeho projekt; Petrova implementace není základem tohoto zadání. Inspirace jeho principem neautorizuje přístup k jeho kódu. Davidův samostatný projekt pro tvorbu videí zůstává mimo rozsah; tento příklad není souhlas do něj zasahovat. Dřívější dodavatelské nabídky byly odmítnuty, kontrola webů není aktuální výchozí zadání.

## Produktová hypotéza a její slabiny

Pracovní popis: **Asistent, který si osvojuje práci ve vašich aplikacích.** Odborně computer-use agent s procedurální pamětí a tvorbou opakovaně použitelných schopností. Pracovní anglický pitch: **An assistant that turns completed work into tested skills and reuses them on new tasks.**

První cílový uživatel k ověření: člověk, který opakovaně provádí podobnou práci ve webových aplikacích, dodržuje vlastní pravidla a dnes musí agentovi znovu vysvětlovat postup nebo opravovat stejné chyby. Správa obsahu může být první oblast, ale poptávka ani ochota platit nejsou ověřené.

Samotné automatické ukládání promptů má slabé odlišení. Obchodní hodnotu by mohlo mít snížení času na zadávání, kontrolování a opravování konkrétní opakované práce. U jednoduchého stálého postupu může vyhrát běžná automatizace; u jednorázové práce může vyhrát obecný agent bez zaučování. Relevantní oblast je opakovaná práce s obměnami a vlastními pravidly.

Neprohlašovat, že každý běh bude rychlejší nebo lepší. Časy 40 → 15 sekund pocházejí z ilustrací v diskusi, nikoli z měření. Upload ani čekání na externí aplikaci se zapamatováním postupu zásadně nezrychlí. Náklady na tvorbu, testování a údržbu schopností je potřeba započítat. Kvalitu názvu videa nelze prokázat jen kontrolou délky nebo tvrzením hodnoticího modelu.

## Co se ukládá a co se musí znovu zjistit

| Vrstva | Příklad | Jakou má roli |
| --- | --- | --- |
| Uživatelská preference | Čeština, věcný tón, bez emoji, konkrétní osnova popisu | Kontext pro práci; sama není novou vykonatelnou schopností |
| Aktuální stav aplikace | Otevřený kanál, nalezené video, formulář a jeho hodnoty | Zjišťuje se při běhu; starý screenshot není aktuální skutečnost |
| Procedurální paměť | Postup nalezení záznamu, úpravy a ověření uložení | Pomáhá vybrat a vykonat správné kroky |
| Ověřená schopnost | Parametrizovaný postup se vstupy, výstupy, oprávněními a testy | Kandidát na registraci a reuse v dalších sessions |

Slovo „YouTube“ nestačí pro výběr schopnosti. Nahrání videa, úprava metadat a odpověď na komentáře jsou jiné operace. Vyhledání musí zohlednit požadovaný výsledek, dostupné vstupy, prostředí, platnost verze a oprávnění. Preference pro jeden kanál se nesmějí automaticky stát pravidlem pro jiný kanál.

MCP je rozhraní k nástrojům, nikoli mechanismus učení. [Playwright MCP](https://github.com/microsoft/playwright-mcp) například zpřístupňuje browser akce a strukturované accessibility snapshoty. Průběžné poznávání potřebných částí aplikace je pro první verzi vhodnější než úplné mapování před prvním úkolem.

## Navržený průchod pro hackathon

David předal kritiku dalšího agenta: první návrh spoléhal na přenos z uploadu do úprav existujícího videa, ale první úkol nemusel přirozeně vytvořit operaci update. Tato námitka je správná. Následující návrh asistenta proto nahrazuje původní dvojici „upload → hromadné úpravy“ dvojicí „dokončení existujícího záznamu → audit a výběrová oprava dalších záznamů“. David tuto změnu ještě nepotvrdil.

Oba úkoly pracují s již nahranými soukromými videi a potřebují číst, kontrolovat a upravovat metadata. Upload by byl až rozšíření mimo hlavní důkaz. Konkrétní aplikace zůstává otevřená; příklad netvrdí funkční podporu YouTube. Podklady, časované přepisy a pravidla jsou dodané vstupy; zpracování řeči ani generování videa nejsou součástí návrhu.

### První session vytvoří schopnosti z uživatelského úkolu

Příklad zadání: **„Dokonči metadata tohoto již nahraného soukromého videa podle dodaných podkladů a pravidel. Zachovej správné části, doplň chybějící odkazy a kapitoly z přepisu, ulož změny a ověř výsledek. Viditelnost videa neměň.“** Příslušný kanál, video a rozsah zápisu musí být určené.

Agent nejprve přečte pravdivý výchozí registr a sám zjistí, které opakovatelné části práce mu chybí. Má základní nástroje pro pozorování, navigaci, kliknutí, vstupy a kontrolu stavu. Základní browser nástroje jsou týmový boilerplate a nesmějí se prezentovat jako jeho výtvor.

Možné rozdělení výsledných schopností, nikoli názvy předepsané runtime promptem:

| Schopnost | Vstup a výstup | Co se prověří |
| --- | --- | --- |
| Přečíst konkrétní video | ID → aktuální strukturovaná metadata a identita záznamu | Správné ID, chybějící záznam, rozpoznání špatného formuláře |
| Zkontrolovat metadata | Metadata, podklady a explicitní pravidla → konkrétní nálezy nebo vyhovující stav | Správná i chybná varianta, povinné odkazy, formát časových značek, povolené zásahy |
| Upravit existující video | ID a změny konkrétních polí → uložený výsledek | Zachování ostatních hodnot a viditelnosti, správný záznam, opakování bez duplicit a nezávislé přečtení výsledku |

Návrh textu může dodat základní model; netvrdit, že samotné psaní českého titulku je nová schopnost. Viditelným samorozšířením mají být opakovatelná práce s aplikací a kontrola konkrétních pravidel. Požadavek „věcný titulek“ má subjektivní část, kterou formální test nevyřeší.

První úkol skutečně potřebuje všechny uvedené operace: přečíst stav → vyhodnotit nedostatky → připravit změny → uložit → přečíst a ověřit. Jestli agent vytvoří pouze jeden monolit pro jediný konkrétní záznam, nelze tvrdit, že vznikly tyto samostatně kombinovatelné schopnosti. Rozdělení musí být vidět ve skutečných artefaktech.

Kandidáti běží v sandboxu. Testovací brána ověří rozhraní a chování na oddělených případech; až potom je povolí registrovat. Agent následně dokončí uživatelův úkol pomocí přijatých schopností. Průzkumné browser kroky mohou tvorbě předcházet. Varianta „nejdřív vše hotovo, potom pouze uložené shrnutí chatu“ nedokládá celý požadovaný průchod.

Browser testy používají izolované testovací prostředí a známé varianty formulářů. Průchod testovacím prostředím neprokazuje kompatibilitu se skutečným YouTube; tu musí potvrdit dokončení a nezávislé přečtení výsledku v cílovém prostředí. Testy nesmějí být opakované nekontrolované zápisy do skutečného kanálu.

### Agent také rozšíří vyhledávání a správu

Tým dodá neměnnou základní vrstvu pro bezpečné uložení kandidáta, kontrolu testů a atomickou aktivaci verze. Návrh rozšíření agentem: malý katalog nad vzniklými manifesty, který umí obnovit index přijatých verzí a vyhledat kompatibilní aktivní schopnosti podle operace, vstupů a prostředí. Obnova indexu představuje konkrétní správu knihovny; vyhledání představuje discovery. Pevnou testovací bránu ani politiku katalog nemění.

Konkrétní potřeba k ověření: po vzniku schopností jsou artefakty uložené, ale základ systému neposkytuje výběr podle jejich nových rozhraní a stavu. Agent při přípravě dalšího použití musí tento nedostatek sám rozpoznat. Není nutné tvrdit, že jde o inovaci nebo velký správní systém; je to povinná část soutěžního prototypu. U malé knihovny by člověku stačil i prostý seznam, takže zákaznickou hodnotu na samotném katalogu nestavět.

Potřeba musí vyplynout z práce s novými schopnostmi a jejich metadaty; nesmí ji nahrazovat skrytý příkaz „teď napiš správce“. Pokud ji agent v demonstraci sám nerozpozná, tato část zadání není splněná. Nevyvolávat umělou poruchu a netvrdit, že vznikla spontánně. Záměrně vložená porucha je označený test.

Generovaný pomocník smí spravovat index v přiděleném registru, nikoli upravovat pevná oprávnění, testovací bránu nebo rozpočtové limity. Test musí vložit manifest přijaté verze, obnovit index a tuto verzi nalézt; po označení za neaktivní ji další obnova a vyhledání nesmějí vrátit. Přidat neslučitelný vstup a jinou operaci. Testovací manifesty jsou označené fixtures, nikoli schopnosti vydávané za naučené z uživatelské práce. Nová session musí prokazatelně zavolat tento generovaný katalog. Návrh mechanismu ještě není důkaz, že jej agent samostatně vytvoří nebo že splní výklad poroty.

### Nová session použije schopnosti pro jinou práci

Restartovat agentní proces a vyčistit konverzační historii. Zachovat jen deklarovaný registr, schválené preference a potřebný stav připojení aplikace.

Druhý příklad zadání: **„Proveď audit těchto dalších čtyř soukromých videí podle stejných publikačních pravidel. Oprav pouze nevyhovující části podle přiložených podkladů. Správná videa nech beze změny a vrať přehled nálezů a skutečných oprav.“**

Agent přes svůj katalog vyhledá dříve vytvořené čtení, kontrolu a úpravy. Nejprve načte a zkontroluje všechny záznamy, rozdělí je podle nálezů, u problémových sestaví a uloží změny a ověří je. Základní orchestrátor smí nově plánovat, větvit a iterovat; nesmí skrýt implementaci chybějící specializované operace do nového kódu.

Výchozí data musejí obsahovat vyhovující i nevyhovující záznam. Důkaz ukáže nezměněné hodnoty u správného záznamu, opravené chyby u dalších, stejné verze a hashe použitých schopností a nulovou tvorbu nových specializovaných schopností ve druhé session. Rozdíl úkolů je dokončení konkrétního záznamu proti auditu a selektivní údržbě kolekce. Jde o omezený přenos v jedné oblasti, ne důkaz zvládnutí libovolné aplikace; dostatečnou odlišnost pro porotu nelze předem garantovat.

## YouTube a volba cílové aplikace

[YouTube Data API podporuje upload i metadata](https://developers.google.com/youtube/v3/docs/videos/insert) a vyžaduje autorizaci. Jeho využití může být praktičtější než ovládání UI; hotový API konektor ale sám neprokazuje učení browser workflow. API nahrání s explicitním `privacyStatus: private` je soukromé video, nikoli totéž co rozepsaný koncept v YouTube Studiu. Tento rozdíl musí být v demu pravdivý.

Pro noční prototyp doporučujeme krátký test proveditelnosti připojení a ovládání cílové aplikace, nikoli dlouhé ladění loginu. Navržený limit je 20 minut od začátku implementačního ověření. Přístup ani účet zatím nejsou ověřené. Při překážce je alternativou dostupný webový redakční systém; samostatná lokální ukázková aplikace je až poslední varianta a musí být označena jako testovací prostředí. Nezobrazovat kopii portálu a netvrdit, že jde o skutečnou integraci.

Nynější konverzace autorizuje návrh a dokumentaci, nikoli skutečný upload či změny videí. Provedení přijde až s konkrétním zadáním, vstupy a určeným účtem. Odevzdání hackathonového demo videa je navíc samostatný proces, ne testovací úloha pro tento produkt.

## Co dovoluje soutěžní brief

Vycházíme ze [záznamu briefu](hackathon-brief.md), ověřeného v přihlášeném [HQ](https://hq.agents007.ai/topics#frankenstein) dne 8. 10. 2026. Tato aktualizace dokumentace není novou kontrolou HQ.

| Činnost | Vztah k zadání |
| --- | --- |
| Uživatel upřesní styl, vstupy, očekávaný výsledek nebo opraví nepochopení | Přípustný vstup do práce; nenahrazuje agentovo rozpoznání mezery |
| Agent uloží preference nebo shrnutí | Užitečné, ale samo nepokrývá vznik otestované schopnosti |
| Agent vytvoří promptový skill s rozhraním, oprávněními a spustitelnými testy | Povolený typ schopnosti; testy musejí ověřovat deklarované chování |
| Člověk napíše celý specializovaný skill | Může být označený výchozí základ; nesmí se vydávat za výtvor agenta |
| Agent registruje kandidáta až po skutečně úspěšných testech | Povinné; log nesmí být pouze text vygenerovaný modelem |
| Člověk schválí registraci | Povoleno; rozpoznání mezery, tvorbu a testování provede agent |
| Jiný úkol v nové session vyhledá a složí dříve vytvořené schopnosti | Povinný důkaz reuse bez ručního propojení |
| Agent vytvoří nebo rozšíří discovery a správu schopností | Povinné; vestavěný seznam frameworku nestačí |

Generovaný kód musí běžet v sandboxu mimo hostitele s přístupovými údaji. Počet iterací a útratu omezí kód, nikoli prompt. Oprávnění zůstanou stejná. Přesné limity jsou dosud nerozhodnuté; implementace musí určit čísla i způsob vynucení před prvním během. Modelové požadavky musí procházet kontrolovanou cestou, aby generovaný kód nemohl rozpočet obejít.

Uživatelská oprava uložené schopnosti vytváří kandidáta nové verze; před aktivací znovu projde testy. Hodnocení stylu oddělit od funkční správnosti a testů oprávnění. Připuštění promptových skills neznamená svolení k neotestovanému přepisování hlavního řídicího cyklu.

## Rozhraní a rozsah první verze

Doporučené rozhraní má zadání s přílohami a pravidly, viditelný browser a stručný průběh: co agent právě dělá, co testuje a jaký výsledek ověřil. Vedle toho knihovna ukazuje novou nebo použitou schopnost, verzi, rozsah a testy. Jde o log akcí a důkazů, nikoli zobrazení skrytého interního uvažování modelu.

Po prvním úkolu má být zřejmé „vznikly tyto ověřené schopnosti“. Po druhém „použily se tyto stejné verze a vznikl tento výsledek“. Pokročilý uživatel může otevřít pravidla a navrhnout změnu. Samotný graf schopností ani počítadlo „AI se zlepšila“ nemají důkazní hodnotu.

**Do první verze patří:** jeden orchestrátor, browser nástroje, sandbox, trvalý registr, testovací brána, agentem vytvořená discovery/správa, vynucené limity, dvě sessions a jednoduché rozhraní s důkazy.

**Odložit:** celodenní nahrávání desktopu, všechny operační systémy, mobilní aplikaci, marketplace, fine-tuning, hlas, tvorbu videa a několik propojených agentních frameworků. CLI může sloužit k vývoji a diagnostice; pro prezentaci je důležitější viditelný výsledek v aplikaci.

## Jak využít AgentFactory a předchozí rešerši

[AgentFactory](https://github.com/zzatpku/AgentFactory) je reference pro vznik, ukládání a opakované používání spustitelných schopností. Přidání tohoto frameworku samo nepřidává hodnotu zákazníkovi. Dřívější statická kontrola revize `df92287894ab7bc9cdfecbd469f4b8a2f4a27616` našla import generovaných modulů do procesu a ukládání bez námi požadované nezávislé povinné testovací brány. Pokud by se použil jako základ, tyto hranice vyžadují řešení; framework zde nebyl spuštěn.

Doporučení pro dnešek: převzít jednoduchý princip knihovny a případně vhodné části implementace po kontrole, neskládat AgentFactory, MUSE a Miguel do vícevrstvého wrapperu. Izolace, testy a účelné UX mají přednost před počtem frameworků. Stack se má určit podle nejkratší ověřitelné cesty k prvnímu úplnému průchodu.

Existující mechanismy nejsou novinka: [Agent Workflow Memory](https://arxiv.org/abs/2409.07429) odvozuje postupy z předchozích úloh; [Record-and-Run](https://github.com/microsoft/Record-and-Run) vychází z demonstrace; [OpenAdapt](https://openadapt.ai/how-it-works) popisuje převod ukázky na program a kontrolu výsledku. Konkurenční výhoda tohoto návrhu je hypotéza o snadnějším zaučení a spolehlivém přenosu zkušenosti, ne doložené prvenství.

Rozšířená lokální rešerše je v `docs/self-extending-agents-research-2026-10-08.md`; při vzniku tohoto podkladu byla necommitnutá. Tento dokument obsahuje klíčové závěry, aby mohl posloužit i samostatně na GitHubu.

## Ověření a podmínky pro zúžení směru

Porovnat stejný model, základní nástroje, vstupní stav a rozpočet ve variantě bez zkušenosti a s ověřenými schopnostmi. Je-li čas, přidat obyčejné textové shrnutí jako další variantu; jinak nepřisuzovat celý rozdíl právě spustitelným skills. Tři různé vstupy a jeden záměrně nekompatibilní případ jsou diagnostika, nikoli statistický důkaz.

Měřit skutečný uložený výsledek, počet zásahů člověka, modelových volání a kroky. Doba uploadu a čekání na aplikaci musí být oddělené od práce agenta. Tvorbu a testování vykázat zvlášť i v celkových nákladech.

Povinné kontroly: selhání testu zabrání registraci; limit ukončí běh; nepovolená operace se neprovede; druhá session použije existující hashe; chybná nebo neaktivní schopnost se nepoužije. Uchovat registr před/po, vykonané testy, původ artefaktů, oprávnění před/po a nezávisle ověřený stav cílové aplikace. Do veřejných důkazů nepatří cookies, tokeny ani cizí osobní údaje.

Pokud uložené schopnosti nezlepší správnost, potřebnou lidskou práci ani počet rozhodnutí oproti základu, nepoužívat tvrzení o přínosu učení. Pokud po prvním technickém bloku nevznikne úplný průchod úkol → vytvoření → test → registrace → výsledek, zúžit cílovou aplikaci a podporované operace; nepřidávat další funkce.

## Časový plán k rozhodnutí

Code freeze i termín odevzdání jsou **9. 10. 2026 v 07:14 Europe/Prague** podle briefu z 8. 10. V 00:10 zbývají přibližně sedm hodin. Doporučený plán, nikoli slib odhadu:

| Do kdy | Výsledek |
| --- | --- |
| 00:30 | Vybraná cílová aplikace, dva úkoly, přínos a cesta k testovatelnému výsledku; konec široké rešerše |
| 00:50 | Ověřený přístup a technický průchod cílovou aplikací, případně rychlá změna cíle |
| 02:15 | První celý průchod včetně sandboxu, testů a registrace; pokud chybí, okamžitě zúžit rozsah |
| 03:30 | Druhá čistá session a doložené skládání; funkční agentem vytvořená discovery a správa |
| 04:45 | Negativní testy, limity, ověření oprávnění a srozumitelný průběh v UI |
| 05:45 | Změřené výsledky, hotové důkazy, návod a stabilní scénář bez nových funkcí |
| 06:30 | Nahrané video do 90 sekund, připravené veřejné repo, odevzdání a anglický pitch |
| 07:14 | Freeze; pozdější commity se nehodnotí |

## Zadání pro dalšího agenta

Kriticky posuď tento pracovní návrh proti Frankenstein briefu a navrhni nejkratší proveditelný úplný průchod. Nevracej odmítnuté náměty a nevybírej další náhodný obor. Rozlišuj Davidem vyslovený záměr, příklady a doporučení asistenta. Nezačínej implementaci bez návazného zadání.

Během nejvýše 15 minut rešerše vrať: doporučenou cílovou aplikaci a důvod; první a odlišný druhý úkol; konkrétní chybějící schopnosti, které z nich mohou přirozeně vzniknout; jak budou testovány, nalezeny a kombinovány; co agent sám přidá do discovery/správy; nejmenší technický základ a největší riziko. Uveď také důvod, proč by obyčejný agent s uloženým promptem mohl být stejně dobrý, a jak to ověřit. Výsledkem má být rozhodnutí použitelné pro build, nikoli další rozsáhlý katalog projektů.
