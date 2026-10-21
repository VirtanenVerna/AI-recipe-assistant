# AI Recipe Assistant

Development of AI Applications -kurssin ryhmäprojekti: resepti-ideoita kotona jo olevista raaka-aineista, paikallisella kielimallilla.

## Team members

- Member 1 Heidi Johansson heidi.johansson@student.hamk.fi
- Member 2 Verna Virtanen verna.virtanen@student.hamk.fi
- Member 3 Elli Lemmetti elli.lemmetti@student.hamk.fi

## Mitä sovellus tekee?

Käyttäjä antaa raaka-aineet ja tämän aterian toiveet. Käyttäjä voi valita annosmäärä henkilöiden mukaan (1-6) ja valmistusajan (15, 30, 45 tai 60min). Sovellus välittää tiedot Ollama kielimallille, joka ehdottaa reseptiä. Erillinen paikallinen muisti säilyttää käyttäjän itse tallentamat ruokavaliot.

Tavoitteena on helpottaa arkista ruoan ideointia ja olemassa olevien raaka-aineiden hyödyntämistä. Tämä on yhden käyttäjän paikallinen demo, ei allergia- tai ravitsemuspalvelu.

## Käyttö

1. **What is in your kitchen?**: raaka-aineet, enintään 4000 merkkiä.
2. **Wishes for this meal**: esimerkiksi annosmäärä tai aikatoive, enintään 1000 merkkiä. Ei tallennu.
3. **Number of servings**: Käyttäjä valitsee haluamansa annosmäärän 1-6.
4.  **Maximum cooking time**: Käyttäjällä on mahdollisuus valita valmistusaika, oletuksena on "No preference", jolloin ei ole aikarajoitusta.
5. **Saved dietary preferences**: pysyvät ruokavaliot. Muokkaaminen ei vielä muuta muistia; paina **Save preferences**.
6. **Suggest a recipe** yhdistää aterian tiedot tallennettuihin ruokavalioihin. Mallia ohjeistetaan pitämään tallennettuja rajoitteita ensisijaisina.
7. **Reset meal fields** tyhjentää aterian kentät, ei muistia.
8. **Forget preferences** poistaa tallennuksen ja tyhjentää sen editorin. Epäonnistuneesta poistosta kerrotaan, eikä editoria tyhjennetä virheellisesti.

Tallennettu ruokavalio näkyy lomakkeessa myös uudelleen avattaessa. Reseptipyyntö ei koskaan kirjoita muistia. Jos muistia ei saada luettua, reseptiä ei generoida: rajoitteita ei ohiteta hiljaa.

## Käynnistys omalla koneella

Tarvitset Gitin, Python 3.12:n (esimerkiksi Minicondan kautta) sekä [Ollaman](https://ollama.com/download/windows).
Asennukset ja mallit ovat konekohtaisia, eivät Git-repossa.

### 1. Nouda uusimmat muutokset main-haarasta

Olemassa olevassa kloonissa:

~~~powershell
git fetch origin
git switch main
git pull --ff-only origin main
~~~

Tee nämä puhtaassa työpuussa tai tallenna ensin omat keskeneräiset muutoksesi. Tarkista lopuksi tila komennolla `git status -sb`.

### 2. Python-ympäristö

Aja projektin juurikansiossa:

~~~powershell
conda env create -f environment.yml
conda activate dev-ai-project
~~~

Jos ympäristö on jo olemassa, älä luo sitä uudelleen:

~~~powershell
conda activate dev-ai-project
python -m pip install -r requirements.txt
~~~

[environment.yml](environment.yml) käyttää conda-forgea ilman Anacondan oletuskanavia.
[requirements.txt](requirements.txt) kiinnittää sovelluksen suorat Python-riippuvuudet testattuihin versioihin. Se ei ole kaikkien transitiivisten riippuvuuksien täydellinen lukitustiedosto.

### 3. Asetukset

PowerShellissä kopioi asetuspohja vain, jos paikallista asetustiedostoa ei jo ole:

~~~powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
~~~

Oletukset:

~~~dotenv
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3.2
OLLAMA_TIMEOUT_SECONDS=120
~~~

[.env.example](.env.example) ja koodin oletus valitsevat molemmat kevyen Llaman.
Omat asetukset ovat Gitin ulkopuolella. PowerShelliin asetettu ympäristömuuttuja ohittaa tiedoston arvon. Käynnistä sovellus uudelleen asetusten muutoksen jälkeen.

### 4. Ollama ja malli

Käynnistä Ollama Windowsin valikosta ja lataa malli kerran:

~~~powershell
ollama pull llama3.2
ollama list
~~~

Jos Ollama-palvelu ei ole käynnissä, aja `ollama serve` omassa terminaalissaan. Älä käynnistä toista palvelinta, jos sama portti on jo käytössä.

### 5. Sovellus

~~~powershell
python -m app.main
~~~

Avaa [http://localhost:7860](http://localhost:7860). Lopeta Ctrl+C:llä.
Päivityksen jälkeen pysäytä vanha sovellus ja käynnistä uudelleen.

### 6. Testit ja arviointi

~~~powershell
python -m pytest -q
python -m evaluation.run --model llama3.2 --output evaluation/my-run.json
~~~

Yksikkötestit eivät tarvitse Ollamaa ja käyttävät eristettyä testimuistia.
Arviointiajo tarvitsee käynnissä olevan mallin, käyttää vain synteettisiä esimerkkejä ja tallentaa vastaukset sekä kestot uuteen raporttiin. Se ei ylikirjoita olemassa olevaa raporttia.

## Mallin valinta

Oletus on `llama3.2`, joka oli kevyempi käyttää kokeillulla koneella.
`qwen3.5:9b` on valinnainen, raskaampi vaihtoehto. Sen noin 6,6 GB:n latauskoko ei kerro koko ajonaikaista muistintarvetta eikä takaa sopivuutta kannettavalle.

Mallin vaihto: lataa haluttu malli, muuta `MODEL_NAME` paikallisessa asetustiedostossa ja käynnistä sovellus uudelleen.
Katso [mallinvalinta ja sen rajat](docs/model-selection.md).

## Rakenne ja dokumentaatio

~~~text
Gradio UI -> UI callbacks -> AIService -> OllamaModelClient -> Ollama
                                |
                                +----> MemoryStore -> paikallinen JSON
~~~

- [Arkkitehtuuri](docs/architecture.md): komponentit, tietovirrat ja virhetilanteet.
- [Päätösloki](docs/project-decisions.md): miksi ratkaisut valittiin.
- [Demo-ohje](docs/demo-guide.md): esittely ja testattavat käyttäjäpolut.
- [Arviointiohje](evaluation/README.md) ja [todelliset tulokset](evaluation/evaluation_results.md).

Ainoa toteutettu lisäkyvykkyys on persistentti ruokavaliomuisti.
[capabilities-kansion](src/capabilities) muut moduulit ovat alkuperäisiä kurssipohjia, eivät toimivia RAG-, MCP-, agentti-, työkalu- tai kuvaominaisuuksia.

## Rajoitteet

- Yksi paikallinen käyttäjä ja yksi muistiprofiili, ei käyttäjätilejä.
- Muisti on salaamatonta JSON:ia. Se ja asetukset on rajattu Gitin ulkopuolelle.
- Mallin vastaus on vapaata tekstiä: ruokavalion noudattamista, ainesosia, määriä tai ruoan turvallisuutta ei varmenneta ohjelmallisesti.
- Mallikutsu käyttää enintään 4096 tokenin kontekstia ja 1024 tokenin tulostusta. Katkaistu tuloste palautetaan virheenä.
- Verkkokutsussa on asetettava aikakatkaisu (oletus 120 s lukuoperaatiolle, yhdistäminen enintään 10 s). Tämä ei ole mallin palvelinpuolinen laskentabudjetti tai sekunnintarkka kokonaiskeston takuu.
- Inferenssi kulkee oletuksena paikalliseen Ollamaan. Gradio-telemetria on poistettu käytöstä ja UI käyttää järjestelmäfontteja. Mallien/pakettien lataaminen tarvitsee verkkoa; ulkoisen mallipalvelimen valitseminen muuttaa tietovirtaa.
- Projektin yhteinen lopullinen versio on `main`-haarassa.
- 
