# Frankenstein — ověřený brief a příprava dema

Stav ověřený **8. října 2026** v přihlášeném HQ. Všechny časy jsou místní pro **Prahu (Europe/Prague)**. Tento dokument je shrnutí zadání a pracovních důsledků, nikoli kopie obsahu portálu.

## Zdroje a jejich role

| Zdroj | Co jsme z něj ověřili |
| --- | --- |
| [HQ — Frankenstein, ground rules a judging](https://hq.agents007.ai/topics#frankenstein) | Definice hotového projektu, povinnosti, nevhodné směry, FAQ, porota, aktuální váhy |
| [HQ — odevzdání](https://hq.agents007.ai/submit) | Povinná pole, veřejné repo, YouTube Unlisted, 90sekundové video |
| [HQ — dashboard](https://hq.agents007.ai/) | Harmonogram a dostupné partnerské nástroje |
| [HQ — tým](https://hq.agents007.ai/team) | Dvoučlenný tým Frankeinsteins, zvolený track, stav propojení repozitáře |
| [Veřejný web](https://agents007.ai/hackathon01/) | Kontext akce a angličtina společného programu; některé údaje se liší od HQ |
| Zadání Davida v tomto projektu | Dva lidé, nejdřív brief a rešerše, následně produkt, 60sekundový pitch a video do 90 sekund |

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

Produkt ani doména zatím nejsou vybrané. Příští krok je rešerše problémů a porovnání nápadů podle těchto otázek a vah poroty.

## Povolené směry a hranice podle HQ

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
3. Jak přesně probíhá minutový pitch: slidy, živé demo, případné dotazy a striktní časový limit?

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

**Živý pitch:** připravujeme **60 sekund podle zadání Davida**. Přesný limit není na přečtených stránkách HQ uveden; konkrétní prezentaci a scénář vytvoříme po výběru produktu. Veřejný web uvádí angličtinu pro společný program a dema.

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
- **Pitch:** minuta pochází od Davida, nikoli z ověřeného textu HQ.
- **Tým a repo:** GitHub repo existuje a je veřejné. Při kontrole 8. 10. týmová stránka HQ stále uváděla, že repozitář není připojený. Jde o zachycený stav, který se může změnit.
- **Produkt:** není vybraný; tento commit dokumentuje pravidla a nezavádí architekturu ani funkčního agenta.

Při změně rozhodnutí nebo upřesnění organizátorů aktualizuj tento dokument i stručné instrukce v `AGENTS.md`. Staré rozpory nemaž tak, aby vznikl dojem, že předchozí neověřené informace byly potvrzené.
