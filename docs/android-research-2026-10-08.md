# Android automatizace — průzkum směru

**Datum:** 8. 10. 2026. **Stav:** pracovní hypotézy, nikoli schválený produkt nebo stack. David doplnil, že Petr má osobní zkušenost s Android automatizací. Jeho konkrétní zaměření a dostupné zařízení zatím nejsou potvrzené. Navazuje na [průzkum problémů](problem-research-2026-10-08.md) a [brief](hackathon-brief.md).

## Pracovní závěr

Android stojí za přednostní ověření díky zkušenosti člena týmu. Ta může zkrátit cestu k funkčnímu demu a dodat reálný příklad problému. Sama však nepotvrzuje poptávku. Potřebujeme určit konkrétní opakovanou práci v konkrétní aplikaci.

Nejslibnější hypotéza pro Frankenstein: agent při řešení mobilního úkolu vytváří, testuje a ukládá použitelné automatizace. V dalším odlišném úkolu je sám najde a zkombinuje. Pro první noc zúžit na jedno zařízení a jednu aplikaci, případně dvě, pokud je Petr již dobře ovládá. Automatické opravy po změně rozhraní mohou být rozšířením; nejsou nutnou součástí první verze.

## Doložené problémy a protiargumenty

### Údržba mobilních testů

V [diskusi r/QualityAssurance](https://www.reddit.com/r/QualityAssurance/comments/1p79cyi/how_do_qa_teams_avoid_the_overhead_of_maintaining/) autor popisuje nespolehlivé testy, kombinace zařízení/prostředí, nekompatibilní verze a dlouhé ladění. Praktický komentář doporučuje soustředit interakce do Page/Screen Objects a dohodnout stabilní identifikátory prvků s vývojáři. Jiný účastník popisuje samostatný tým pro infrastrukturu.

To podporuje existenci údržbové práce, nikoli závěr, že ji agent celou vyřeší. Infrastruktura, skutečná chyba aplikace a změněný identifikátor jsou odlišné příčiny. Diskuse obsahuje i propagaci nástrojů; její příspěvky nejsou reprezentativním průzkumem ani ověřenými údaji o firmách.

### Osobní automatizace a Tasker

V [r/tasker](https://www.reddit.com/r/tasker/comments/1kjtcip/autoinput_accessibility_setting_keeps_breaking/) uživatel popisuje opakované výpadky AutoInput a nutnost ručně obnovovat accessibility službu. Ostatní zmiňují podobné zkušenosti i odlišné chování zařízení. Jde o historický popis konkrétních konfigurací; dnešní stav opravy jsme neověřovali.

Pro návrh je důležité nezaměňovat tuto potíž za chybějící automatizační postup. Nefunkční systémová služba nebo chybějící oprávnění se nemusí spravit vygenerováním nového postupu. Podle briefu navíc samorozšiřování nesmí zvětšovat oprávnění.

## Co už existuje

| Projekt | Doložená schopnost | Důsledek pro náš návrh |
| --- | --- | --- |
| [Droidrun / Mobile Harness](https://github.com/droidrun/mobile-harness) | Podklady a API pro ovládání Androidu/iOS, lokální Android přes ADB či Portal, práce s UI a agentovou pamětí | Samotné ovládání telefonu agentem a ukládání poznámek nejsou dostatečný vlastní přínos. README označuje projekt jako harness, nikoli samostatný agentní runtime. |
| [AppAgentX](https://appagentx.github.io/) a [oficiální kód](https://github.com/Westlake-AGI-Lab/AppAgentX) | Z historie interakcí rozpoznává opakované sekvence a vytváří vyšší akce pro jejich znovupoužití | Také samotný nápad „agent se učí mobilní postupy“ má přímého předchůdce. Musíme konkrétně předvést vlastní přínos; netvrdit prvenství. |
| [AndroidWorld](https://github.com/google-research/android_world) | Prostředí a benchmark na živém emulátoru, úlohy v reálných aplikacích a kontrola výsledku | Možný vzor pro opakovatelné ověření. Není důkaz zákaznické poptávky. Celý benchmark nemusíme integrovat; dokumentace upozorňuje na omezení Docker varianty na Apple Silicon. |

Projekty byly posouzené z dokumentace, nikoli prakticky otestované nebo kompletně bezpečnostně prověřené. Nebyly instalované žádné nové skills ani mobilní nástroje. Případné převzetí infrastruktury je nutné odlišit od schopností, které za běhu vytvoří náš agent. Neověřili jsme, že konkurence postrádá testování, verzování nebo skládání schopností; tyto vlastnosti proto nejsou potvrzenou tržní výlučností.

## Dvě hypotézy podle Petrovy zkušenosti

1. **Petr automatizuje běžnou práci v aplikacích:** pomoci lidem, kteří stále opakují stejný mobilní postup. Vybrat jeho skutečný případ, například přenos záznamů mezi používanými aplikacemi, pokud takovou práci opravdu řeší. Změřit ruční zásahy, správnost a využití dříve vytvořených schopností. Zatím nemáme doloženého uživatele ani konkrétní proces.
2. **Petr testuje Android aplikace:** pomoci malému týmu vytvářet a znovu používat kroky regresních scénářů. Ověřit, zda ho zatěžuje psaní/údržba postupů, nebo infrastruktura. Pokud už má stabilní Appium testy, musí být zřejmé, co navíc získá. Agent nesmí upravovat očekávaný výsledek jen proto, aby test prošel.

## Ilustrační demo pro druhou hypotézu

Jde o návrh konstrukce dema, nikoli výběr konkrétní aplikace nebo potvrzený zákaznický problém.

- **Úkol A:** v aplikaci pro úkoly založit zadání s termínem a ověřit uložený obsah. Z úkolu vyplyne potřeba naučit se například vytvoření a čtení záznamu. Agent příslušné schopnosti skutečně vytvoří a otestuje na izolovaném stavu. Jejich podobu nesmí dostat předem nadiktovanou jako hotovou implementaci.
- **Vznik správy:** agent vytvoří nebo rozšíří vyhledávání schopností podle aplikace, vstupů/výstupů a podmínek použití. Pevně napsané menu ani pouhé uložení do registru samo nesplňuje tento bod briefu.
- **Úkol B, nová session:** z dodaného seznamu doplnit pouze chybějící úkoly, zachovat existující a ověřit výsledný seznam. Agent má najít a zkombinovat dřívější čtení a vytváření bez jejich přegenerování a ručního propojení.
- **Důkazy:** registr před/po, artefakty vytvořených schopností, testovací logy, správný výsledný stav, verze použité v druhé session a stejná oprávnění. Měřit i čas a modelová volání, ale neslibovat úsporu před měřením.
- **Případné rozšíření:** změnit rozložení testovací aplikace a ověřit adaptaci interakce při stejném očekávaném výsledku. Skutečně nefunkční uložení musí zůstat selháním. Toto rozšíření přidat až po fungujícím základním průchodu.

Tento příklad prokazuje mechanismus, ale sám má slabý produktový příběh. Nahradit jej reálným postupem z Petrovy zkušenosti, pokud je dostupný. Prohlášení „Android agent pro všechny aplikace“ by pro jednu noc bylo příliš široké.

## Co potřebujeme od Petra

- Poslední konkrétní automatizace: aplikace, vstup, požadovaný výsledek a místo, kde se člověk musí zapojit.
- Používané nástroje a funkční telefon/emulátor dostupný dnes.
- Co ho stojí nejvíc práce: vytvoření postupu, jeho opravy, opakované klikání, nebo provoz zařízení.

Generovaný kód musí být v sandboxu odděleném od hostitele s přístupovými údaji. Samotný fakt, že cílová aplikace běží v emulátoru, tuto podmínku ještě nesplňuje. Přístup k zařízení musí zůstat uvnitř předem daných oprávnění; počet iterací a útrata se omezují kódem podle briefu.
