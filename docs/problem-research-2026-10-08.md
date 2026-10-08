# Rešerše problémů pro Frankensteina

**Datum:** 8. 10. 2026. **Stav:** průzkumný shortlist; produkt není zvolený ani ověřený u zákazníka. Navazuje na [soutěžní brief](hackathon-brief.md).

**Pozdější doplnění:** Petr má zkušenost s Android automatizací. [Navazující průzkum Androidu](android-research-2026-10-08.md) zohledňuje tuto informaci; doporučení níže vzniklo před ní a není závazným výběrem produktu.

## Pracovní doporučení

Pro první prototyp na jednu noc doporučuji **agenta pro opakované zpracování dodavatelských souborů**, zúženého na malý e-shop nebo distributora. Alternativa s dobrým příběhem je **srovnávání nesourodých cenových nabídek**. Oprava automatizací má silnou vazbu na technické zadání, ale větší integrační riziko.

Jde o můj úsudek podle dostupných dokladů, rozsahu pro dva lidi a možnosti předvést skutečné rozšiřování schopností. Nejde o zjištění, že první varianta má největší trh nebo nejvyšší ochotu platit. Velká část základních funkcí už existuje; originalita musí stát na konkrétním vlastním přínosu.

## Jak byla rešerše provedena

- Cílené vyhledávání a čtení veřejných diskusí na Redditu, Shopify Community a n8n Community.
- Sledované oblasti: převody zákaznických dat, dodavatelské katalogy, nákup a porovnání nabídek, údržba automatizací, agenturní reporting, školní komunikace pro rodiče, ukládání webového obsahu a zpracování fotografických výstupů.
- Kontrola současné nabídky podle oficiální dokumentace a produktových stránek. Produkty nebyly prakticky otestované.
- Větší váhu mají konkrétní popisy vlastní práce a omezení. Výzkumné otázky zakladatelů a propagační komentáře nejsou samy o sobě potvrzením poptávky.
- Hledány byly také protiargumenty: hotová řešení, standardizace vstupů, nedostatečně častý problém a případy, kdy postačí jednoduchá šablona.
- Nic nebylo zveřejněno ve fórech, nikdo nebyl kontaktován. Nebyly instalované nové third-party skills.

**Limity:** výběr je účelový, převážně anglickojazyčný a není reprezentativní. Identita a deklarovaná zaměstnání autorů nejsou ověřené. Časy v příspěvcích jsou jednotlivá tvrzení, ne průměry trhu. Komentáře mohou být marketing nebo generovaný obsah. Starší vyřešená chyba není důkaz současné neopravené chyby. Není ověřená ochota cílových zákazníků zaplatit nám ani situace na českém trhu.

## Přehled kandidátů

Následující hodnocení je kvalitativní úsudek, nikoli naměřené skóre nebo prognóza poroty.

| Směr | Signál problému | Vazba na Frankenstein | Rozsah na noc | Hlavní slabina |
| --- | --- | --- | --- | --- |
| Dodavatelské soubory pro e-shop/distributora | Opakovaný napříč datovým a obchodním kontextem | Silná: generování a skládání převodů, kontrol a discovery | Relativně zvládnutelný při práci pouze se soubory | Velmi přímá konkurence; samotné AI mapování nestačí |
| Porovnání cenových nabídek | Konkrétní popisy práce ve dvou oborových komunitách | Silná, pokud vzniknou skutečně opakovaně použitelné schopnosti | Střední; zúžit typ nabídky a dokumenty | Význam položek, příplatků a rozsahu může být nejednoznačný |
| Opravy automatizací po změně formátu | Doložené případy i současné diskuse | Silná: nový adaptér a validátor, opakované skládání | Rizikovější s plnou integrací do n8n | Hotový AI builder, jednoduché opravy a náklady na integrace |
| Rodičovský organizátor školních zpráv | Silný subjektivní problém | Slabší: mnoho úloh zvládne běžná extrakce a kalendář | Zvládnutelný prototyp, integrace přidají práci | Přímá konkurence; obtížné doložit nutnost nových schopností |
| Agenturní reporting | Doložená ruční práce, ale i funkční automatizace | Střední při nových transformacích, slabá u pouhého shrnutí | Střední bez reklamních API | Hotové produkty; hodnota často spočívá v úsudku specialisty |

## 1. Agent pro dodavatelské soubory — doporučený první směr

### Co lidé skutečně popisují

V [diskusi datových specialistů z července 2024](https://www.reddit.com/r/dataengineering/comments/1e6xy1q/how_do_you_handle_messy_data_from_customers/) autor řeší proměnlivé názvy a pořadí sloupců v souborech zákazníků. Nechce znovu stavět vlastní křehký převodník a výslovně píše o zájmu zaplatit za existující řešení. To je jednotlivý signál ochoty platit, nikoli validovaná objednávka.

[Další diskuse z prosince 2025](https://www.reddit.com/r/dataengineering/comments/1pojhd1/how_to_deal_with_messy_excelcsv_imports_from/) popisuje opakované jednorázové skripty kvůli nekonzistentním souborům. Komentáře doporučují i odmítání vadných dat a předem dohodnuté formáty. Technologické řešení tedy není vždy nejlepší odpověď.

Obchodní kontext potvrzuje [dotaz provozovatele připravovaného e-shopu](https://community.shopify.com/t/how-can-i-integrate-multiple-dropship-suppliers-with-various-formats-in-my-ecommerce-store/40995): různí dodavatelé posílají různé formáty produktů, zásob i cen. V [diskusi ze září 2026](https://community.shopify.com/t/how-do-you-handle-supplier-spreadsheets-when-updating-your-store/676989) účastníci řeší párování produktů, kontrolu změn a riziko chybného přepsání dat. Tuto novější diskusi zahájil vývojář zkoumající trh a obsahuje propagaci nástrojů; bereme ji jako doplněk, ne nezávislý průzkum zákazníků.

### Hypotéza produktu — náš návrh

**Pro koho:** člověk, který opakovaně dostává soubory od více dodavatelů a nemůže všem nadiktovat jeden formát.

**Úkol uživatele:** „Z těchto nových ceníků mi připrav změny vůči našemu katalogu a ukaž položky, které je potřeba zkontrolovat.“

**Přínos:** jednou naučený a otestovaný převod zůstane použitelný pro další zakázky; uživatel dostane kontrolovatelný seznam změn, ne pouze odpověď v chatu. Úsporu času a snížení chyb musíme teprve změřit.

### Konkrétní scénář pro Frankensteina

1. Uživatel nahraje současný katalog a dva dodavatelské soubory s různým členěním. Zadá požadovaný obchodní výsledek, nikoli seznam nástrojů k napsání.
2. Agent zkontroluje registr a zjistí, které převody a kontroly postrádá. V sandboxu vytvoří například adaptér dodavatele a normalizaci balení/jednotek s testy; podoba schopností musí vzniknout z úkolu.
3. Agent vytvoří nebo rozšíří discovery/správu, například index schopností podle podporovaných vstupních a výstupních schémat a kontrol jejich kompatibility. Nestačí připravené menu nástrojů.
4. Po testech nainstaluje schopnosti a vytvoří přehled změn s dohledatelným původem hodnot a výjimkami.
5. V nové session dostane jiný úkol: „Pro tento seznam zboží porovnej dodavatele podle ceny za kus a dostupného množství.“ Zkombinuje dřívější adaptéry a normalizaci, bez ručního propojení a bez přegenerování.

**Rozsah na noc:** jeden jednoduchý katalog, dva dodavatelské formáty, několik desítek řádků, jedna měna a explicitně uvedené balení. Vstup a výstup v souborech; automatický zápis do produkčního e-shopu není potřebný k této definici výsledku. Případná demo data označit jako syntetická.

**Kontrola:** zachování identifikátorů včetně úvodních nul, žádné změny nedotčených položek, správné jednotkové ceny podle ručně ověřeného vzorku, odmítnutí neznámé jednotky. „Skladem“ neznamená známý počet kusů; chybějící cenu nebo význam sloupce nesmí agent vymyslet. Měřit správnost, počet ručních zásahů a znovupoužití existujících verzí; rychlost druhého běhu nepředstírat.

### Konkurence a důvod případného zamítnutí

- [Stock Sync](https://help.stock-sync.com/en/article/how-do-i-correctly-map-fields-in-my-product-feed-1ny1trw/) již nabízí mapování dodavatelských polí; jeho návod řeší i změny hlaviček a převod nestandardních hodnot pomocí pravidel.
- [Matrixify MCP](https://matrixify.app/documentation/matrixify-mcp-server/) výslovně dokumentuje import dodavatelského souboru pomocí AI agenta, který data převede kódem. To je přímé překrytí se základním nápadem.
- [Flatfile / Obvious — Mapping](https://flatfile.com/product/mapping/) a [Flatfile Transform](https://flatfile.com/news/flatfile-announces-transform-an-advanced-agentic-experience-for-data/) popisují automatické mapování, učení z předchozích importů a agentní transformace. Obecné „AI opraví CSV“ nemůže být naše tvrzení o originalitě.

**Hypotéza odlišení:** viditelné vznikání, testování, verzování a skládání specializovaných schopností napříč úkoly, s ovládáním operátorem. Rešerše nepotvrdila, že toto konkurence neumí. Před pitchem je potřeba vysvětlit vlastní implementovaný přínos bez tvrzení „jsme první“.

**Zamítnout, pokud:** pro vybraný scénář stačí jedna uložená šablona nebo Matrixify s agentem nabídne stejnou hodnotu a neumíme ukázat nic dalšího. Stejně tak pokud je celé demo jen přejmenování tří sloupců.

## 2. Agent pro srovnávání nesourodých nabídek

### Doložený problém

V [r/procurement](https://www.reddit.com/r/procurement/comments/1nnhsbn/how_do_you_handle_bid_comparisons/) člověk zapojený do výběrového řízení popisuje převádění různých dokumentů do společné tabulky. Jiný účastník uvádí nesrovnatelné cenové základy: cena za stránku versus dokument a jazykové příplatky. To je problém významu a kalkulace, nejen formátu.

V [r/estimators](https://www.reddit.com/r/estimators/comments/1jk85xd/talk_to_me_about_your_love_of_bid_leveling_gc/) několik lidí používá Excel i vedle placeného softwaru, protože potřebují vlastní strukturu a návaznost na rozpočet. Popisy cen a velikosti firem nejsou ověřené. Důležitý závěr pro návrh: výsledkem může být tabulka zapadající do jejich práce, ne povinná migrace na novou platformu.

### Hypotéza a demo

**Uživatel:** menší nákupní tým nebo koordinátor, který potřebuje srovnat nabídky jednoho typu služby či zboží.

**Úkol 1:** „Srovnej tyto tři nabídky pro stejnou objednávku; rozliš základní cenu, dopravu a volitelné položky.“ Agent vytvoří chybějící extraktory a normalizátory, otestuje je a zachová odkaz na konkrétní řádek nebo místo zdrojového dokumentu.

**Úkol 2 v nové session:** jiné množství nebo nová objednávka u stejných dodavatelů. Agent najde kompatibilní dřívější schopnosti a zkombinuje je pro jiný propočet. Vytvořená správa musí umožnit kontrolu verze a použitelnosti nástrojů.

**Rozsah:** jeden druh nákupu, například tisk či balicí materiál; nejprve textové/CSV nabídky, textové PDF pouze pokud zůstane čas. Neřešit celý stavební rozpočet, právní výklad podmínek ani automatické zadání objednávky.

**Kontrola:** nesčítat volitelné položky do základu, nezaměnit cenu za balení a kus, neprezentovat chybějící údaj jako nulu. Pokud bez upřesnění nelze nabídky srovnat, označit konkrétní chybějící vstup. Nevyhlašovat absolutního vítěze jen podle neúplných cen.

**Konkurence/protiargument:** sourcing software existuje; [Opstream](https://www.opstream.ai/) nabízí širší agentní procurement platformu. [Praktici v diskusi o nabídkách](https://www.reddit.com/r/procurement/comments/1mi7m8k/how_do_you_compare_supplier_quotes_still_manual/) doporučují vlastní povinnou šablonu nebo Power Query; někteří s nimi už problém téměř nemají. Zaměřit se proto na konkrétní zbylou výjimku, nikoli slib vyřešit veškerý procurement.

**Verdikt:** srozumitelný příběh pro porotu, ale ověřování věcného významu bude těžší než u úzce definovaných katalogových dat.

## 3. Agent opravující automatizace po změně dat

### Doložený problém

[n8n Community, březen 2025](https://community.n8n.io/t/llm-basic-chain-output-format/90943) obsahuje konkrétní případ změny struktury výstupu, po níž uživatel hlásil 43 rozbitých workflows. **Tato konkrétní chyba byla následně opravena**; nelze ji prezentovat jako současnou neopravenou chybu n8n.

[Diskuse ze srpna 2026](https://community.n8n.io/t/how-do-you-catch-workflows-that-run-fine-but-do-nothing/308708?tl=en) řeší běhy bez chyby, které nedodají očekávaná data. Autor později zmiňuje vývoj vlastního řešení, takže jde o částečně komerčně motivovaný zdroj. Komentáře zároveň ukazují, že část problému řeší obyčejné kontroly výsledku a společný monitoring.

### Hypotéza a demo

**Uživatel:** správce automatizací, kterému cizí zdroj mění datovou strukturu.

**Úkol 1:** „Zpracuj tyto záznamy a vytvoř report.“ Průchod narazí na nepodporovanou strukturu; agent vytvoří adaptér a kontrolu obchodního výsledku, otestuje je a dokončí úkol.

**Úkol 2:** nová session a jiný tok používající kombinaci dřívějšího adaptéru a validátoru. Agentem rozšířený index vyhledá kompatibilní vstup/výstup, operátor vidí důvod opravy a může ji vrátit.

**Rozsah:** malý izolovaný runner a vstupy reprodukující dva typy změny. Simulované API tak označit; problém je reálný, ale demo není důkaz provozu u zákazníka. Integrace do celého n8n není nutná pro prototyp a výrazně zvětšuje rozsah.

**Kontrola:** neznámá data se nesmějí zahodit jen proto, aby byl běh zelený. Převod musí zachovat význam a být ověřený na nezávislých příkladech. Změna autorizace, expirovaný token nebo nejasný význam nejsou problém, který lze vyřešit přepsáním adaptéru.

**Konkurence:** [n8n AI Workflow Builder](https://docs.n8n.io/build/ways-of-building-workflows/ai-workflow-builder.md) již umí vytvářet, upravovat a ladit workflows přirozeným jazykem. Prosté „AI opraví workflow“ tedy není novinka. Rozdíl by musel být v kontrolovaném vytváření trvalých schopností, regresních testech a přenosu mezi úlohami.

**Verdikt:** silné technické demo; pro tým bez zkušenosti s konkrétní platformou větší riziko, že většinu noci zabere infrastruktura.

## Dva další směry, které bych teď neupřednostnil

### Školní zprávy a rodinný kalendář

[Rodiče popisují zahlcení školními e-maily](https://www.reddit.com/r/workingmoms/comments/1vnr34y/overwhelmed_by_school_emails/), ruční přesouvání termínů a rozdělování povinností. Příležitost by byla v rozpoznání změněného termínu, příprav před akcí a vazeb mezi zprávami. [Ohai](https://www.ohai.ai/features/ai-email-management/) však už nabízí zpracování e-mailů a dokumentů do událostí a úkolů. U prototypu by bylo obtížnější ukázat, proč musel agent skutečně vytvořit novou schopnost místo běžné extrakce. Ponechat jako variantu, pokud se objeví konkrétní neřešený scénář.

### Měsíční reporting agentur

[r/PPC](https://www.reddit.com/r/PPC/comments/1myo7la/client_reporting_feels_way_more_manual_than_it/) potvrzuje ruční práci, ale také existující úspěšnou automatizaci sběru a sestavení reportů. Část zbývající práce je odborná interpretace. [AgencyAnalytics](https://agencyanalytics.com/features/smart-reports) už nabízí automatické reporty z integrací. Samotný další generátor shrnutí by měl slabé odlišení a nemusel by prokázat samorozšiřování.

## Co ověřit před závazným výběrem

1. **S garantem tracku:** ukázat dva konkrétní uživatelské úkoly, vznikající schopnosti a agentem vytvořenou správu. Ověřit, že se nejedná pouze o základní funkce zvoleného frameworku.
2. **S někým z praxe, pokud je na místě:** požádat o popis posledního skutečného souboru/zakázky. Co přesně musel ručně opravit? Jak často? Jaké řešení používá? Co by musel vidět, aby výsledku důvěřoval? Nestačí otázka „líbí se ti nápad?“.
3. **Technickou zkouškou po volbě směru:** ověřit sandbox, tvorbu alespoň dvou užitečných schopností, selhávající test a úspěšné znovupoužití po nové session. Člověkem připravené referenční vstupy a očekávané výsledky nesmějí obsahovat předem napsanou schopnost vydávanou za výtvor agenta.
4. **Proti existujícím řešením:** formulovat jednu konkrétní vlastnost, kterou jsme skutečně postavili navíc. Pokud se nápad scvrkne na „nahraj soubor do AI“, zúžit nebo změnit směr.

## Připravený popis pro rozhovor s porotcem

> We are exploring an agent for small businesses that repeatedly receive supplier files in incompatible formats. A real task makes it create and test missing adapters and data checks, and extend its capability discovery. In a fresh session, a different purchasing task combines those capabilities without manual wiring. We will show the registry, test evidence, and unchanged permissions. Is that a convincing interpretation of the ecosystem requirement?

Toto je návrh k diskusi, nikoli finální minutový pitch ani tvrzení o již fungujícím produktu.
