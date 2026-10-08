# Zadání nezávislého posouzení projektu pro Claude

**Stav k 9. 10. 2026 přibližně 00:40 Europe/Prague.** David žádá nezávislý, upřímný názor na produktový směr pro hackathon. Posuď, zda stojí za další práci, jaký má přínos oproti dostupným řešením a zda jej lze v daném čase věrohodně předvést. Doporučení předchozích asistentů jsou hypotézy určené ke kritice; nemusíš s nimi souhlasit. Tvým výstupem je posouzení, nikoli zahájení implementace.

Repozitář: [drewn-ed/007FrankensteinAgent](https://github.com/drewn-ed/007FrankensteinAgent). Jde o veřejné podklady k sólo projektu. Není zde funkční implementace navrženého agenta. David pracuje sám; Petr na tomto projektu nespolupracuje a Stitch není součástí tohoto zadání. Davidův jiný projekt pro tvorbu videí zůstává mimo rozsah.

## Čti v tomto pořadí

| Dokument | Účel |
| --- | --- |
| [AGENTS.md](../AGENTS.md) | Pravidla práce, aktuální kontext a závazné hranice produktu |
| [Hackathon brief](hackathon-brief.md) | Podmínky soutěže, hodnocení, harmonogram a požadované výstupy |
| [Produktový návrh](learning-agent-product-blueprint-2026-10-09.md) | Aktuální celkový koncept, užitečné navazující funkce, role agentů a otázka škálovatelnosti |
| [Kritická rešerše self extending agentů](self-extending-agents-research-2026-10-08.md) | Existující projekty, původní zdroje, limity výzkumných výsledků a statická kontrola vybraných implementací |
| [Technický handoff](learning-browser-agent-handoff-2026-10-09.md) | Pracovní návrh dema, připomínky dalšího agenta a testovatelné hranice; není definicí celého produktu |
| [Vývoj konceptů](learning-agent-concepts.md) | Jak se měnily úvahy; obsahuje i starší návrhy, které nejsou aktuálním zadáním |

Starší [průzkum problémů](problem-research-2026-10-08.md) je doplňkový kontext. [Nabídky dodavatelů](solo-project-proposal.md) jsou Davidem odmítnutý návrh; nepřebírej jej jako současný plán. Časové plány ve starších dokumentech mohou být při čtení již zastaralé.

## Kontext eventu a aktuální stav

Jde o **Agents 0.0.7 — From Dusk Till Dawn #01**, track **Frankenstein**, v noci z 8. na 9. října 2026. Code freeze a odevzdání jsou **9. 10. v 07:14 Europe/Prague**. K času tohoto podkladu zbývá přibližně 6 hodin 34 minut; při posouzení pracuj s aktuálním zbývajícím časem.

Před freeze musí být odevzdané veřejné repo a **YouTube Unlisted video do 90 sekund s běžícím produktem**. David požaduje také **60sekundový anglický živý pitch**; tento čas pochází od něj, nikoli z přečteného HQ. Hodnocení z HQ: hodnota a relevance 35 %, originalita 25 %, funkční úplný průchod 20 %, technické provedení 10 %, validace a limity 10 %.

Zdroj soutěžních podmínek je přihlášený [HQ brief](https://hq.agents007.ai/topics#frankenstein) a [formulář](https://hq.agents007.ai/submit), ověřené 8. 10.; obsah shrnuje místní brief. Starší veřejný web měl jiné váhy a délku videa. Pokud HQ nemáš dostupné, nevydávej místní záznam za svou novou kontrolu HQ.

Povinný průchod: skutečný úkol vyvolá agentovo rozpoznání chybějící schopnosti → agent ji vytvoří, provede spustitelné testy, po úspěchu zaregistruje a dokončí úkol → sám rozšíří také vyhledávání a správu schopností → jiný úkol v čisté session vyhledá a zkombinuje dříve vzniklé schopnosti bez jejich opětovné tvorby a ručního propojení. Oprávnění se nezmění.

Generovaný kód musí běžet v sandboxu, instalaci blokují neúspěšné testy, iterace a útratu omezuje kód. Skill může být kód, MCP server či promptový balíček, ale potřebuje rozhraní, deklarovaná oprávnění a spustitelné testy. Frameworky jsou povolené; předem napsanou infrastrukturu nelze vydávat za schopnost vytvořenou agentem. Fine-tuning vah, triviální funkce a neotestované přepisování hlavního řídicího cyklu jsou mimo zadání. Přiznávají se simulace, selhání a nehotové části.

## Co David chce vytvořit

Pracovní prostředí s asistentem, kterému uživatel zadá práci v aplikaci. Agent se při jejím řešení zorientuje, vytvoří potřebné postupy a z vlastní zkušenosti nebo oprav uživatele získává opakovaně použitelné schopnosti. V dalších úkolech je sám vyhledává, kombinuje a případně přiděluje dílčí práci specialistům. Modelové váhy se měnit nemusí.

Širší produkt tvoří projekty s podklady a pravidly, zadání a viditelný průběh práce, učení z konkrétních oprav, knihovna „co už umím“, opakované použití postupů a později rutiny či sdílení v týmu. Počet agentů a skills není cílová metrika. Hypotéza hodnoty je méně opakovaného vysvětlování, ručních zásahů a oprav při dalších skutečných úkolech.

Davidovi záleží na silném UX a přesvědčivé prezentaci. Širší vize a malý funkční demonstrační průchod mají být jasně odlišené. Dobře natočený koncept není důkazem funkčního runtime. Samotná implementace je dosud otevřená; není potvrzený název, stack, účet ani cílová integrace. V konverzaci vznikl rozkliknutelný koncept obrazovek, ale není to běžící agent ani integrace.

**YouTube, Meta Ads, DaVinci a dříve Bakaláři jsou pouze příklady možných aplikací.** Neredukuj celý projekt na přepisování YouTube metadat. Zároveň nemusíš potvrdit univerzální podporu všech aplikací; posuď, jaký rozsah by byl věrohodný a užitečný.

## Jak jsme se k tomu dostali

1. David chtěl odborně pojmenovat směr a najít existující vzory. Jedním z podnětů byl [redditový příspěvek o Miguelovi](https://www.reddit.com/r/SideProject/comments/1rq1w0c/i_built_a_selfimproving_ai_agent_it_started_with/).
2. Probírali jsme AgentFactory, MUSE, Miguel a další systémy. David nechce znovu vynalézat základ, ale použít vhodné existující řešení a přidat skutečnou hodnotu.
3. Zvažoval se produkt, který sleduje lidskou ukázku a naučí se workflow. Následně David zdůraznil učení z práce vykonané samotným agentem; lidská ukázka může být pomocná cesta.
4. Inspirací byl Davidův popis jiného řešení ovládajícího telefon přes accessibility rozhraní. Neznáme ověřenou implementaci ani benchmarky tohoto řešení. Časy 40 → 15 sekund či 40 → 5–10 sekund jsou ilustrace, nikoli výsledky našeho projektu.
5. Předchozí asistent příliš soustředil diskusi na úzké demo. David jej opravil: chce posoudit celkový produkt, užitečné rozšiřující funkce, škálovatelnost a zájem uživatelů. Proto vznikl produktový návrh, který má přednost před domněnkou, že YouTube je vybraný niche.
6. Další agent identifikoval tři slabiny původního dema: upload nevytváří automaticky schopnost úpravy; styl psaní není důkaz samorozšíření; vlastní discovery a správa existují zatím jen jako plán. Handoff nyní navrhuje práci s existujícími záznamy v obou sessions. Jde o opravený návrh, ne spuštěný důkaz ani uživatelem potvrzenou integraci.

## Co víme z rešerší

| Projekt | Možná role | Důležité omezení dosavadních závěrů |
| --- | --- | --- |
| [AgentFactory](https://github.com/zzatpku/AgentFactory) | Spustitelní specialisté, ukládání a reuse | Ve staticky kontrolované revizi chyběla naše požadovaná izolace a nezávislá povinná testovací brána; není hotovým řešením celého briefu |
| [MUSE Autoskill v2](https://arxiv.org/html/2605.27366v2) | Životní cyklus, katalog a paměť ke konkrétní schopnosti | V2 má testy volitelné; ověřený oficiální runtime jsme nenainstalovali. Benchmarky mají podstatné podmínky a omezené pokrytí |
| [AutoSkill](https://github.com/ECNU-ICALK/AutoSkill) a SkillEvo | Zkušenosti a opravy → verze skills; hodnocení kandidátů | Ukládání opravy není samo důkaz funkčního zlepšení ani splnění instalační brány |
| [Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Blízký konkurent i reference celkového produktu | Již řeší velkou část skills, paměti, delegování, rutin a správy; obecný seznam těchto funkcí není odlišení |
| [Miguel](https://github.com/soulfir/miguel) | Inspirace samorozšiřováním a historií | Široká self-modifikace a dříve nalezené hranice testování, oprávnění a spouštění kódu; dosud nedoporučen jako hlavní základ |
| [Record and Run](https://github.com/microsoft/Record-and-Run), [OpenAdapt](https://openadapt.ai/how-it-works), [Agent Workflow Memory](https://arxiv.org/abs/2409.07429) | Demonstrace, browser workflow a učení postupů | Základní nápad je známý; samotné sledování obrazovky, replay a ukládání zkušeností nejsou novinka |

Podrobné zdroje a statické revize jsou v rešerši a handoffu. **Žádný z těchto frameworků jsme v této rešerši nespustili; cizí benchmarky jsme nereprodukovali.** Zhodnoť také možnost, že hotový základ s obyčejnou pamětí splní uživatelskou potřebu dostatečně dobře. Není nutné použít všechny uvedené projekty nebo přijmout doporučení některého z předchozích asistentů.

## Poslední SWOT a stav důkazů o zájmu

| Oblast | Dosavadní pracovní posouzení, které můžeš zpochybnit |
| --- | --- |
| Silné stránky | Srozumitelný příslib menší opakované práce; reuse a skládání; viditelné učení má demonstrační potenciál |
| Slabé stránky | Široký cílový uživatel, neověřené odlišení, nákladné zaučení a kontrola, náročnost spolehlivé exekuce |
| Příležitosti | Lidé a malé týmy s vlastními opakovanými postupy; rutiny; předávání know-how kolegům |
| Hrozby | Funkční překryv s konkurencí; změny aplikací; chybné akce; provozní náklady a ruční servis, který brání škálování |

Existují dodavatelské zákaznické příběhy o poptávce po automatizaci, například [Lindy a Truemed](https://www.lindy.ai/case-study/truemed). Nejde o nezávislé ověření našeho produktu ani ochoty za něj platit. **Nemáme zákaznické rozhovory, placený pilot, měření retence ani vlastní důkaz časové úspory.** Dosavadní závěr asistenta byl „smysluplná hypotéza pro MVP, zatím slabě obhájená konkurenční výhoda“; neber jej jako požadovaný výsledek své recenze.

Navržené ověření srovnává stejný model, nástroje a výchozí stav bez zkušenosti, případně s prostým shrnutím, a s ověřenými schopnostmi. Sleduje správný výsledek, čas člověka včetně kontrol, počet zásahů, cenu vytvoření a údržby a přenos na vhodný i nevhodný nový případ. Pouhý rychlejší druhý běh nebo vyšší počet skills nestačí.

## Co má tvoje posouzení zodpovědět

1. **Verdikt:** pokračovat, zásadně zúžit, nebo změnit směr? Uveď nejsilnější důvod pro doporučení a nejsilnější argument proti němu. Odděl zajímavost pro hackathon od dlouhodobé životaschopnosti.
2. **Uživatel a hodnota:** kdo by produkt opakovaně používal, za jaký konkrétní přínos by platil a co používá dnes? Rozliš důkaz, odhad a věc vyžadující ověření.
3. **Konkurence a originalita:** co už umí relevantní dostupný základ a jaký vlastní přínos zde zbývá? Nepovažuj vznik skills, agentní delegaci ani hezký dashboard za automatickou výhodu.
4. **Ucelený produkt:** které nejvýše tři navazující funkce nejvíce podporují hlavní užitek a které dnes odstranit? Posuzuj celkové pracovní prostředí; malý demo scénář není jediný možný trh.
5. **Škálování:** kde vznikne ruční servis, provozní cena nebo závislost na aplikacích? Co by muselo platit, aby to byl opakovatelně nasaditelný produkt?
6. **Soutěž a proveditelnost:** které požadavky máme pouze popsané a jak by je prokázal nejmenší funkční průchod ve zbývajícím čase? Zvlášť prověř přirozený vznik discovery/správy a skutečnou kombinaci starších schopností v nové session.
7. **Další krok:** navrhni jeden levný experiment s měřitelným výsledkem a podmínkou, při které doporučíš nápad opustit nebo změnit. Pokud doporučíš pivot, vysvětli, který problém opravuje a proč bude v daných podmínkách lepší.

Vrať výsledek česky, začni verdiktem a dej přednost konkrétním námitkám a rozhodnutím před opakováním dokumentace. Cíleně ověř klíčová sporná tvrzení v primárních zdrojích; není potřeba další rozsáhlý katalog projektů. Uveď, které podklady se ti podařilo přečíst a co jsi nemohl ověřit. Nezačínej build, neinstaluj skills a neměň externí účty v rámci tohoto posouzení.
