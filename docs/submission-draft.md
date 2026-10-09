# Podklad k odevzdání — pracovní verze

**Není odesláno do HQ. Název a cílový scénář jsou návrh, nikoli potvrzené rozhodnutí Davida.**

## 1. Název a jednovětý pitch

Pracovní název: **Proofwork**. Dostupnost názvu ani značky není prověřená.

> Proofwork turns your corrections into tested, reusable skills for the next task.

Česky: Proofwork převádí tvoje opravy na otestované schopnosti, které agent využije při další práci.

## 2. Co produkt dělá, pro koho a jaký problém řeší

Návrh textu; cílového uživatele a pracovní scénář je ještě potřeba potvrdit:

Proofwork je pracovní prostředí pro lidi, kteří opakovaně zpracovávají data a podklady a musí AI znovu vysvětlovat stejné opravy. Uživatel zadá skutečný úkol. Když agentovi chybí potřebný postup, vytvoří vykonatelnou schopnost, otestuje ji v izolovaném prostředí a uloží pro další práci. Když uživatel výsledek opraví, systém se pokusí převést opravu na konkrétní test a přijme novou verzi jen tehdy, když projde novým i předchozími testy. V nové session má agent uložené schopnosti najít a kombinovat. Rozhraní ukazuje výsledek práce, původ schopností a skutečné výsledky kontrol.

První technický rozsah je zpracování explicitně vložených dat a textových souborů. Ovládání YouTube, jiných webů nebo desktopu zatím není součástí implementace. Poptávka a ekonomický přínos nejsou doložené zákaznickými rozhovory ani srovnávacím měřením.

## 3. Co skutečně funguje od zadání po výsledek

Stav průběžně aktualizovat až po ověření:

- Připojení k Gemini 3.5 Flash-Lite bylo ověřeno skutečným generováním JSON odpovědi.
- Free tarif projektu potvrdil David. Klíč je pouze v ignorovaném lokálním .env.
- Docker běží; Python image byl stažen.
- Devět infrastrukturních testů prošlo: izolace bez sítě a klíče, zákaz rozšíření oprávnění, blokace chybné verze, časové a výstupní limity, trvalý registr, oprava s regresními testy a zákaz předání kódu v metadatech autorovi testů. Jde o označené testovací fixtures.
- První skutečný běh Gemini vytvořil schopnost pro zpracování registrací, prošel třemi sandboxovými testy a uložil verzi 1. Další krok skončil HTTP 503. Nový proces následně schopnost použil beze změny a dokončil úkol.
- Přes webové rozhraní agent skutečně očistil tři syntetické registrace na dva jedinečné záznamy, uložil schopnost a vrátil výsledek. U těchto prvních testů byla nalezena netěsnost: popis schopnosti obsahoval i kód. Neoznačujeme je za nezávislé; oprava brání předávání nadbytečných polí autorovi testů.
- Oprava na syntetickém případu zabránila sloučení dvou lidí bez emailu. Původní verze testem neprošla; dvě skutečně vygenerované opravy prošly všemi pěti testy. Verze 2 byla přijata se stejnými oprávněními. Nový test měl explicitně stanovený správný výsledek; nevygeneroval jej testovaný kód.

Tento seznam zatím není finální text pole „funguje“. Před odevzdáním jej nahradit konkrétním zaznamenaným scénářem, výsledkem a jeho limity.

## 4. Co je simulované, chybí nebo je nespolehlivé

Aktuální návrh pravdivých limitů:

- Cílový pracovní proces a finální produktové zaměření nejsou potvrzené.
- Neovládáme browser ani desktopové aplikace. Nové schopnosti mají pouze výpočetní oprávnění nad dodanými daty.
- Modelový autor testů může nesprávně interpretovat zadání; úspěšné testy nezaručují obecnou správnost ani nemožnost škody.
- Trvalý registr sám nedokazuje agentem vytvořené vyhledávání/správu. Tuto část i skládání v nové session musíme prokázat skutečným během.
- Bezplatná kvóta Gemini může běh zastavit. Žádný automatický placený fallback není nastavený.
- Syntetické vstupy a infrastrukturní testovací implementace budou označené; nesmějí být vydávány za reálnou zákaznickou práci ani tvorbu modelu.
- Zrychlení, nižší cena, zákaznická poptávka a převaha nad běžným agentem zatím nejsou prokázané.

## 5. Odkazy

- Pracovní veřejný repozitář: https://github.com/drewn-ed/007FrankensteinAgent
- Implementace se nyní připravuje lokálně na větvi `codex/learning-agent-mvp`; veřejné zveřejnění aktuálního kódu je potřeba ověřit před odevzdáním.
- Demo video: **zatím nevytvořeno**. Požadavek HQ: YouTube Unlisted, maximálně 90 sekund, běžící produkt, přiznané limity.

## Dokončení před HQ

- [ ] Potvrzený název a jednovětý pitch.
- [ ] Potvrzený uživatel, problém a konkrétní demo.
- [ ] Pole 2 do 3 000 znaků; pole 3 a 4 každé do 2 000 znaků.
- [ ] Povinný Frankenstein průchod ověřený skutečným během a novou session.
- [ ] Repo veřejně obsahuje ověřený kód a návod, bez přístupových údajů.
- [ ] YouTube Unlisted video funguje a má nejvýše 90 sekund.
- [ ] HQ skutečně odeslané tlačítkem Submit a poslední commit pushnutý před 07:14.
