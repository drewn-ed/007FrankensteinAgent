# Frankenstein — ověřený brief a příprava dema

Stav ověřený **8. října 2026** v přihlášeném HQ. Všechny časy jsou místní pro **Prahu (Europe/Prague)**. Tento dokument je shrnutí zadání a pracovních důsledků, nikoli kopie obsahu portálu.

**Doplnění 9. 10. 2026:** David v chatu předal zprávu organizátorů „SUBMITTED VIDEOS vs. ON-STAGE PITCHES“. Níže je zachycen její význam pro video a pitch; původní odkaz ani datum vydání zprávy nebyly dodány. Jde o předaný zdroj, nikoli nové ověření původní zprávy v HQ.

**Kontrola při přípravě dokumentace 9. 10. 2026:** v přihlášeném HQ byly znovu přečteny Frankenstein, ground rules, váhy hodnocení a formulář odevzdání. Povinný průchod, váhy, limity textů 3 000 / 2 000 / 2 000 znaků, YouTube Unlisted do 90 sekund a uzávěrka 07:14 odpovídají tomuto briefu. Formulář byl neodeslaný DRAFT s prázdnými projektovými poli a odkazy. Aktuální anglické podklady jsou v [indexu dokumentace](README.md), zejména [průvodci pro porotu](jury-guide.md) a [textech do formuláře](submission-draft.md). Starší produktové úvahy níže jsou historický kontext; aktuální implementaci popisuje hlavní README. Zpráva o minutovém živém pitchi tímto nebyla nově ověřena v původním zdroji.

## Zdroje a jejich role

| Zdroj | Co jsme z něj ověřili |
| --- | --- |
| [HQ — Frankenstein, ground rules a judging](https://hq.agents007.ai/topics#frankenstein) | Definice hotového projektu, povinnosti, nevhodné směry, FAQ, porota, aktuální váhy |
| [HQ — odevzdání](https://hq.agents007.ai/submit) | Povinná pole, veřejné repo, YouTube Unlisted, 90sekundové video |
| [HQ — dashboard](https://hq.agents007.ai/) | Harmonogram a dostupné partnerské nástroje |
| [HQ — tým](https://hq.agents007.ai/team) | Tehdejší stav registrace týmu, zvolený track a propojení repozitáře; David nyní pracuje sólo |
| [Veřejný web](https://agents007.ai/hackathon01/) | Kontext akce a angličtina společného programu; některé údaje se liší od HQ |
| Zadání Davida v tomto projektu | David pracuje sólo; nejdřív brief a rešerše, následně produkt, 60sekundový pitch a video do 90 sekund |
| Zpráva organizátorů „SUBMITTED VIDEOS vs. ON-STAGE PITCHES“, vložená Davidem do chatu 9. 10. 2026 | Video 90 s vysvětluje porotě postavený produkt; pitch 60 s představuje myšlenku, relevanci, originalitu a hodnotu. Doporučení 1–2 nejsilnějších sdělení kvůli sérii přes čtyřicet minutových pitchů. Původní odkaz nebyl dodán. |

Za pracovní zdroj pravdy pro soutěžní parametry bereme aktuální HQ. Novější výslovné upřesnění organizátorů má být zaznamenáno a promítnuto do obou dokumentů.

## Co znamená dokončený Frankenstein

Zadání míří na **užitečný ekosystém schopností**, který agent sám rozšiřuje a umí používat i v dalších sessions. Důležitý je vznik schopnosti z potřeby konkrétního úkolu, její ověření a pozdější skládání s dalšími schopnostmi.

Povinný průchod a technické hranice jsou v [AGENTS.md](../AGENTS.md). Při návrhu se ptej zejména:

- Jaký problém má konkrétní uživatel a jak pozná zlepšení?
- Co agent původně neumí a jak to zjistí z úkolu?
- Jak vznikne otestovaná schopnost s jasným rozhraním a oprávněními?
- Jak agent přispěje k vyhledávání a správě schopností nad rámec hotového frameworku?
- Co nového zvládne po spuštění další session bez ruční pomoci?
- Jak prokážeme, že nový výsledek vznikl kombinací dřívějších schopností a se stejným rozsahem oprávnění?

**Poslední směr podle Davida, synchronizovaný 8. 10. přibližně 23:59:** Frankenstein sólo. Rozvíjí [agenta, který si osvojuje práci v aplikacích z vlastního řešení úkolů, případně lidských ukázek](learning-agent-concepts.md). Bakaláři jsou pouze příklad; konkrétní use case, odlišení a stack nejsou vybrané. Kontrola webů je dřívější návrh, ne výchozí zadání. Nový produkt a název nejsou potvrzené. Tyto změny nemění soutěžní povinnosti výše; změnu týmu v HQ je potřeba vyřešit s organizátory. Frankenstein brief byl dříve během diskuse znovu přečten v přihlášeném HQ; povinnosti a váhy zůstaly shodné s tímto dokumentem. Synchronizace chatů není novým ověřením HQ.

## Povolené směry a hranice podle HQ

**Aktualizace směru 9. 10.:** David chce pokračovat v učenlivém pracovním asistentovi a žádá celkovou produktovou koncepci. [Nový produktový návrh](learning-agent-product-blueprint-2026-10-09.md) odděluje širší funkce, škálovatelnost a noční MVP; YouTube, Meta Ads a DaVinci zůstávají příklady. Stack ani konkrétní integrace nejsou potvrzené. Tato aktualizace nemění soutěžní požadavky ani nepředstavuje nové ověření HQ.

Smysluplné směry zahrnují odhalování chybějících schopností, generování nástrojů/MCP serverů/skills, automatické testování, trvalý registr, verzování, rollback a agentem vytvořené nástroje pro discovery a správu. Vizuální, akční nebo hlasové schopnosti jsou volitelné.

Do soutěžního výsledku se nepočítá pouhé routování mezi předem připravenými nástroji ani prezentace toho, co už umí základní framework. Tým může dodat základ systému, ale nesmí podvrhnout vlastní kód jako nově vygenerovanou schopnost. Triviální ukázkové funkce, fine-tuning a neotestované zásahy do řídicího cyklu či systémového promptu jsou mimo zamýšlený rozsah.

Framework lze použít; porota hodnotí vlastní mechanismus rozšiřování. Instalace hotového marketplace skillu prokazuje instalaci, nikoli vytvoření schopnosti. Lidská schvalovací brána je přípustná, ale nesmí suplovat agentovo odhalení mezery, tvorbu a testy.

## Společná pravidla akce

- Tým může mít jednoho až tři lidi. Každý člen potřebuje registraci Luma a registraci v HQ.
- Projekt vzniká od kick-offu; open-source knihovny, frameworky a vlastní boilerplate jsou povolené.
- Před uzávěrkou odevzdejte repozitář i video v HQ. Pozdější commity se do hodnocení nepočítají.
- Přiznejte simulace, nehotové části a limity.
- Duševní vlastnictví zůstává týmu. Open source je podporovaný; samotné zveřejnění repozitáře neurčuje jeho licenci.
- Soutěžíme ve Frankensteinu. Inspirace dalšími tracky nemění jeho podmínky; obecné požadavky na rešerši osob či agentní platby nepřebíráme jako povinnosti tohoto projektu.

Pro kontext byly přečteny všechny tři tracky: Social Media Deep Research řeší výzkum osoby/organizace pro určitý cíl s doložitelnými zdroji; Agentic Economy řeší provedené transakce a spolupráci agentů; Frankenstein řeší tvorbu a opětovné skládání schopností. Jejich speciální podmínky nejsou zaměnitelné.

## Hodnocení

| Kritérium podle aktuálního HQ | Váha | Co si připravit jako důkaz — naše doporučení |
| --- | ---: | --- |
| Hodnota a relevance k tracku | 35 % | Konkrétní uživatel, problém, užitečný výsledek a skutečná potřeba samorozšíření |
| Originalita | 25 % | Srozumitelně vysvětlit vlastní přínos nad frameworkem a existujícími nástroji |
| Funkčnost od vstupu po výstup | 20 % | První úkol včetně vzniku schopností a jiný úkol v nové session |
| Technické provedení | 10 % | Přiměřená architektura, sandbox, testy, registr a vynucené limity |
| Validace a pravdivé limity | 10 % | Pozorované výsledky, důkazy, přiznané nedostatky a selhání |

Každý porotce používá škálu 0–5. Celkem: `Σ (skóre / 5 × váha)`, tedy maximálně 100 bodů. Užitečnost a originalita dohromady tvoří 60 %; zároveň bez povinného funkčního průchodu není splněn brief.

## Porota a mentoři našeho tracku

- **David Bečvařík — Etnetera**, mentor a porotce; Discord `rwngwn`. HQ uvádí přítomnost zpravidla do půlnoci a přespání na místě.
- **Luděk Šafář — prg.ai**, mentor a porotce. Časová dostupnost není v přečteném briefu upřesněná.
- Partner tracku: **Etnetera**, téma navržené organizátory.

Naše doporučené otázky pro osobní rozhovor, nikoli nevyřešené podmínky blokující práci:

1. Splňuje náš konkrétní návrh dostatečně agentem vytvořené discovery a správu, nebo příliš spoléhá na hotový framework?
2. Je náš druhý úkol dostatečně odlišný a je kombinace vzniklých schopností přesvědčivá?
3. Jaké jsou technické podmínky minutového pitche: slidy, živé demo a případné dotazy? Délku 60 sekund a zaměření potvrzuje zpráva organizátorů předaná Davidem 9. 10.

## Časy a výstupy

| Kdy | Událost podle HQ |
| --- | --- |
| Čt 8. 10., 17:30 | Kick-off |
| Čt 8. 10., 18:25 | Západ slunce a pizza |
| Čt 8. 10., 21:00 | Plánovaný začátek buildování |
| Pá 9. 10., 00:00 | Půlnoční občerstvení |
| **Pá 9. 10., 07:14** | **Code freeze a uzávěrka odevzdání** |
| Pá 9. 10., 08:00 | Snídaně |
| Pá 9. 10., 10:00 | Prezentace |
| Pá 9. 10., 11:30 | Vyhlášení |
| Pá 9. 10., 12:00 | Zakončení |

**Odevzdání v HQ:** veřejný GitHub repozitář a funkční odkaz na YouTube video s viditelností **Unlisted**, maximálně **90 sekund**. Formulář požaduje ukázku běžícího produktu, ne samotné slidy. Draft se ukládá automaticky; lze jej upravovat do 07:14, ale je potřeba projekt skutečně odeslat tlačítkem Submit.

Doporučená struktura videa přímo v HQ: **15 sekund problém a uživatel → 60 sekund kompletní demo → 15 sekund co je skutečné, simulované a co zbývá**. Čekání lze zrychlit, selhání se nesmějí vystříhat. Marketingový úvod tedy musí nechat dost času na důkaz funkčnosti.

**Upřesnění organizátorů předané Davidem 9. 10. — video versus živý pitch:**

- **Video, 90 sekund:** vysvětlení pro porotu, co během noci vzniklo. Může být techničtější a popisné; ukazuje skutečně postavený produkt, jeho mechanismus a výsledek. Povinný Frankenstein průchod a přiznání limitů nadále platí.
- **Pitch na pódiu, 60 sekund:** myšlenka, její relevance, originalita a hodnota pro uživatele. Organizátoři odkazují na otázky u nejvýše vážených kritérií v HQ/Topics. Kvůli rychlé sérii přes čtyřicet minutových pitchů doporučují **1–2 nejsilnější zapamatovatelná sdělení**.

**Naše produkční interpretace:** připravit tři související výstupy se společným příběhem a vizuály: soutěžní video s vysvětlením funkčnosti a důkazy; minutový pitch s problémem, uživatelem, přínosem a originalitou; samostatný launch film pro landing page. Délka launch filmu zatím není rozhodnutá ani předepsaná organizátory. Dlouhý marketingový úvod nesmí vytlačit potřebné důkazy ze soutěžního videa. Konkrétní demo scénář zůstává otevřený a musí odpovídat skutečným schopnostem enginu. Veřejný web uvádí angličtinu pro společný program a dema; Davidovo produktové rozhodnutí vyžaduje angličtinu i pro video a slidy.

### Pole formuláře pro odevzdání

| Pole | Povinnost / omezení |
| --- | --- |
| Název projektu | Povinné |
| Jednovětý pitch | Povinné |
| Co produkt dělá | Povinné; problém, uživatel a řešení; max. 3 000 znaků |
| Co funguje od vstupu po výstup | Povinné; max. 2 000 znaků |
| Co je simulované, chybí nebo je křehké | Povinné; max. 2 000 znaků |
| Stack a partnerské nástroje | Volitelné |
| Veřejný GitHub repozitář | Povinné |
| Odkaz na živé demo | Volitelné |
| YouTube Unlisted video | Povinné; do 90 sekund |
| Best ElevenLabs Use | Volitelná účast checkboxem |
| Zobrazení projektu, videa a repa ve veřejných výsledcích | Samostatný checkbox; při kontrole byl zaškrtnutý |

### Pracovní checklist pro pozdější ověření

Toto jsou plánované kontroly; nezaškrtnuté položky netvrdí, že už projekt existuje.

- [ ] Jasný uživatel, problém, přínos a odlišnost od dostupných řešení.
- [ ] Registr před během ukazuje skutečný výchozí stav.
- [ ] Reálný úkol vyvolá rozpoznání mezery bez pevného pokynu k tvorbě určitého nástroje.
- [ ] Agent vytvoří schopnosti a nástroje pro jejich discovery/správu; původ artefaktů je doložitelný.
- [ ] Generovaný kód běží v odpovídajícím sandboxu; úspěšné testy předcházejí instalaci a jsou v logu.
- [ ] První úkol skončí užitečným výsledkem.
- [ ] Jiný úkol v nové session zkombinuje dřívější schopnosti bez ručního propojení či opětovné tvorby.
- [ ] Oprávnění se nezmění; omezení iterací a útraty jsou v kódu a ověřená.
- [ ] Operátor vidí stav a má skutečnou kontrolu; limity a selhání jsou přiznané.
- [ ] Veřejné repo obsahuje postup spuštění a relevantní důkazy, žádné přístupové údaje.
- [ ] Odkaz na repo je uložený na týmové stránce HQ a ve formuláři odevzdání.
- [ ] Video má nejvýše 90 sekund, správnou viditelnost a porota ho může přehrát.
- [ ] Povinná pole jsou vyplněná a projekt je skutečně odeslaný před freeze; nestačí uložený draft.
- [ ] Poslední hodnocený commit je pushnutý před 07:14 a zaznamenaný.
- [ ] Pitch je nacvičený na 60 sekund a jeho tvrzení odpovídají demu.

## Dostupné nástroje — pouze informace, ne zvolený stack

- **Apify:** HQ nabízí 100 USD kreditu na scraping/webová data, s uplatněním jednou za tým a omezeným počtem účtů.
- **ElevenLabs:** individuální kupon přes oficiální Discord; volitelná samostatná cena **Best ElevenLabs Use**, kterou vybírá **Vláďa Beran**. Hlas nepřidávej pouze kvůli logu partnera.
- **Masumi / Sokosumi:** HQ nabízí 5 000 kreditů, přibližně 50 USD.

Konkrétní kódy a přístupové údaje zůstávají v HQ. Použití partnerů není v přečteném Frankenstein briefu stanoveno jako povinné. Dostupnost kreditů sama neznamená, že byly uplatněné.

## Rozpory a aktuální stav

- **Váhy:** veřejný web uváděl 35 % funkčnost / 25 % hodnotu / 20 % techniku / 10 % originalitu / 10 % validaci. Přihlášené HQ uvádí tabulku výše. První chatové shrnutí vycházelo z veřejného webu; pro další práci je tímto opravené.
- **Video:** veřejný web uváděl dvě minuty; HQ brief i formulář shodně uvádějí **nejvýše 90 sekund**. Používej 90 sekund.
- **Pitch:** při ověření HQ 8. 10. minuta pocházela pouze od Davida. Zpráva organizátorů „SUBMITTED VIDEOS vs. ON-STAGE PITCHES“, kterou David předal 9. 10., nově potvrzuje **60 sekund** a zaměření na relevanci, originalitu a hodnotu. Původní odkaz nebyl dodán; netvrdíme, že jsme tuto zprávu nezávisle přečetli v HQ.
- **Tým a repo:** GitHub repo existuje a je veřejné. Při kontrole 8. 10. týmová stránka HQ stále uváděla, že repozitář není připojený. Jde o zachycený stav, který se může změnit.
- **Produkt:** David pracuje sólo a nový produkt není potvrzený. Finální tým a odkaz pro odevzdání je nutné sladit se skutečným stavem; žádná změna v HQ zde nebyla provedena.

Při změně rozhodnutí nebo upřesnění organizátorů aktualizuj tento dokument i stručné instrukce v `AGENTS.md`. Staré rozpory nemaž tak, aby vznikl dojem, že předchozí neověřené informace byly potvrzené.
