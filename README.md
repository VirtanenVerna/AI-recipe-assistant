# AI recipe assistant

Starter template for the **Development of AI Applications** course final group project.

## Team members

- Member 1 Heidi Johansson heidi.johansson@student.hamk.fi
- Member 2 Verna Virtanen verna.virtanen@student.hamk.fi
- Member 3 Elli Lemmetti elli.lemmetti@student.hamk.fi


## Problem
Mitä tänään syötäisiin?

### Intended users
Sovellus on tarkoitettu ihmisille, jotka haluavat löytää helppoja reseptejä jo kotoa löytyville raaka-aineille.

### Problem statement
Kotoa usein löytyy kaapeista raaka-aineita, mutta ruokaideat loppuvat kesken. Sopivan reseptin etsiminen vie aikaa ja saattavat vaatia uusia raaka-aineita. Sovelluksen tarkoituksena on helpottaa sopivan ruoan löytämistä ja samalla auttaa hyödyntämään jo olemassa olevia raaka-aineita.

### Why AI is appropriate
Tekoäly soveltuu ongelmaan, koska käyttäjä voi antaa raaka-aineensa ja toiveensa. Kielimalli pystyy tulkitsemaan käyttäjän antamia tietoja ja muodostamaan niiden perusteella erilaisia reseptiehdotuksia. 

## Solution
Sovellus on tekoälyä hyödyntävä reseptisovellus. Käyttäjä kertoo sovellukselle mitä raaka-aineita häneltä löytyy ja tarvittaessa antaa esimerkiksi ruokavalioon tai ruoan ominaisuuksiin liittyviä toiveita.

Sovellus käyttää kielimallia tietojen käsittelemiseen ja ehdottaa niiden perusteella sopivaa ruokaa. Se antaa käyttäjälle reseptin, tarvittavat raaka-aineet ja valmistusohjeet.

## Main user workflow

1. **User Input:** Käyttäjä syöttää Gradio-käyttöliittymään käytettävissä olevat raaka-aineet ja mahdolliset ruokatoiveet.
2. Memory: Sovellus tarkistaa käyttäjästä aikaisemmin tallennetut ruokavalioon ja ruokamieltymyksiin liittyvät tiedot.
3. **Processing & Guardrails:** Sovellus yhdistää käyttäjän syöttämät raaka-aineet, toiveet ja tallennetut mieltymykset mallille annettavaan pyyntöön.
4. **Model Response:** Kielimalli muodostaa käyttäjälle sopivan reseptiehdotuksen.

## Architecture

Below is the initial starter architecture. As your project evolves with additional capabilities, replace or extend this diagram in [`docs/architecture.md`](docs/architecture.md).

```text
User
  ↓
Gradio UI (app/ui.py)
  ↓
Application / AI Service (src/services/ai_service.py)
  ↓
Model Client (src/models/model_client.py)
  ↓
Ollama (Local LLM Server)
```

> **Core Architectural Rule:** The user interface must NEVER communicate directly with the model client or Ollama. All interactions must pass through the service layer (`ai_service.py`).

## Model

- **Model used:To be determined / local Ollama model
- **Selection rationale: Malli valitaan projektin kehityksen aikana testaamalla sovellukseen sopivaa paikallisesti toimivaa mallia.

## Additional AI capability

Select at least one additional capability to implement for your final project:

- [ ] RAG (Retrieval-Augmented Generation)
- [ ] Tools / External API integration
- [ ] Model Context Protocol (MCP)
- [ ] Agentic workflow (Model-selected actions based on observations)
- [x] Memory / Persistent state
- [ ] Multimodal interaction (Text + Images)
- [ ] Other: ______________________

### Capability justification
Memory-ominaisuuden avulla sovellus voi muistaa käyttäjän ruokavalioon ja ruokamieltymyksiin liittyviä tietoja. Käyttäjän ei tällöin tarvitse syöttää samoja tietoja jokaisella käyttökerralla uudelleen. Esimerkiksi kasvissyöjänä oleva käyttäjä voi tallentaa ruokavalionsa, jolloin sovellus huomioi sen automaattisesti tulevissa reseptiehdotuksissa. Memory tekee sovelluksesta henkilökohtaisemman ja helpomman käyttää.

## Setup

### 1. Create the Conda environment

```bash
conda env create -f environment.yml
```

### 2. Activate the environment

```bash
conda activate dev-ai-project
```

### 3. Configure environment variables

Copy `.env.example` to create your local `.env` configuration file:

On Linux / macOS:
```bash
cp .env.example .env
```

On Windows (Command Prompt / PowerShell):
```powershell
copy .env.example .env
```

Ensure `.env` contains valid values for `OLLAMA_BASE_URL` and `MODEL_NAME`:
```env
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3.2
```

### 4. Start Ollama

Make sure Ollama is installed and running locally, then pull your configured model:

```bash
ollama run llama3.2
```

### 5. Run the application

Run the application from the root directory of the project:

```bash
python -m app.main
```

Then open your browser at `http://localhost:7860`.

### 6. Run automated tests

```bash
pytest
```

## Evaluation

Describe your evaluation methodology and summarize key results. Starter test cases can be found in [`evaluation/test_cases.json`](evaluation/test_cases.json).

Refer to [`evaluation/README.md`](evaluation/README.md) for guidelines on defining success, edge cases, and failure scenarios.

## Known limitations

- Highlight known system limitations, unhandled edge cases, or boundaries of current capabilities.

## Future improvements

- List planned feature enhancements, architectural refactorings, or future capabilities.
