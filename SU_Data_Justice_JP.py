streamlit run SU_Data_Justice_JP.py

import os
import streamlit as st
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

st.set_page_config(page_title="Persona Chatbot", page_icon="💬", layout="wide")

os.environ["GROQ_API_KEY"] = st.secrets.get("GROQ_API_KEY", "VUL_HIER_JE_API_KEY_IN")

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.5
)

# ---------------- SCHEMA'S ----------------
class ChatAntwoord(BaseModel):
    persona_naam: str = Field(description="Naam van de persona die antwoord geeft")
    antwoord: str = Field(description="Antwoord vanuit het perspectief van die persona")
    uitleg: str = Field(description="Korte uitleg waarom deze persona gekozen is")

class CheckSchema(BaseModel):
    score: int = Field(description="Score van 0 tot 100")
    toelichting: str = Field(description="Maximaal één zin uitleg bij de score")

class PersonaSchema(BaseModel):
    naam: str = Field(description="Naam van de persona")
    samenvatting: str = Field(description="Korte neutrale beschrijving van de persona")
    kenmerken: list[str] = Field(description="Lijst van gedragskenmerken of eigenschappen")
    bias: CheckSchema = Field(description="Bias-check")
    hallucinaties: CheckSchema = Field(description="Hallucinatie-check")
    inclusie: CheckSchema = Field(description="Inclusie-check")
    totaalscore: int = Field(description="Gemiddelde van de drie scores afgerond")

class GegenereerdePersona(BaseModel):
    naam: str = Field(description="Volledige naam van de persona")
    doelgroep: str = Field(description="Doelgroep waartoe deze persona behoort")
    leeftijd: int = Field(description="Leeftijd in jaren")
    achtergrond: str = Field(description="2-3 zinnen over wie deze persoon is")
    uitdagingen: list[str] = Field(description="2-4 concrete uitdagingen of behoeften")
    gedrag: list[str] = Field(description="2-4 gedragskenmerken relevant voor UX")

class PersonaSetSchema(BaseModel):
    personas: list[GegenereerdePersona]

# ---------------- PROMPTS ----------------
generator_prompt = ChatPromptTemplate.from_messages([
    ("system", "Je bent een expert in het ontwerpen van inclusieve UX-personas."),
    ("human",
     "Genereer personas op basis van deze opdracht.\n\n"
     "Opdracht:\n{opdracht}\n\n"
     "Regels:\n- Elke persona is uniek en specifiek.\n"
     "- Gevarieerd in leeftijd, geslacht en culturele achtergrond.\n"
     "- Uitdagingen zijn concreet en verifieerbaar.\n"
     "- Geen stereotypen of vooroordelen.\n\n"
     "Geef ALLEEN een JSON object terug met veld: personas.")
])

validator_prompt = ChatPromptTemplate.from_messages([
    ("system", "Je bent een Bias-Justice validator gespecialiseerd in het beoordelen van synthetische UX-personas."),
    ("human",
     "Beoordeel de persona systematisch op bias, hallucinaties en inclusie.\n\n"
     "Scoreschaal: 0-70 problematisch, 71-80 aandacht nodig, 81-100 goed.\n\n"
     "Persona:\n{persona}\n\n"
     "Geef alleen gestructureerde output terug.")
])

chat_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Je bent een chatbot die antwoord geeft vanuit de gegenereerde persona’s. "
     "Gebruik alleen de persona-context. Antwoord alsof je de best passende persona bent."),
    ("human",
     "Hier zijn de persona’s:\n{persona_context}\n\n"
     "Vraag van de gebruiker:\n{vraag}\n\n"
     "Antwoord alsof je de meest relevante persona bent.")
])

# ---------------- FUNCTIES ----------------
def persona_naar_tekst(p: GegenereerdePersona) -> str:
    uitdagingen = "\n".join(f"- {u}" for u in p.uitdagingen)
    gedrag = "\n".join(f"- {g}" for g in p.gedrag)
    return f"""{p.naam}, {p.leeftijd} jaar, {p.doelgroep}
{p.achtergrond}
Uitdagingen:
{uitdagingen}
Gedrag:
{gedrag}"""

def maak_persona_context(evaluatieset):
    stukken = []
    for naam, tekst in evaluatieset:
        stukken.append(f"NAAM: {naam}\n{tekst}")
    return "\n\n".join(stukken)

def kleur_label(score: int) -> str:
    if score <= 70:
        return "ROOD"
    if score <= 80:
        return "GEEL"
    return "GROEN"

def genereer_personas(opdracht: str):
    structured_generator = llm.with_structured_output(PersonaSetSchema, method="json_mode")
    chain = generator_prompt | structured_generator
    return chain.invoke({"opdracht": opdracht})

def valideer_persona(tekst: str):
    structured_validator = llm.with_structured_output(PersonaSchema, method="json_mode")
    chain = validator_prompt | structured_validator
    return chain.invoke({"persona": tekst})

def chatbot_vraag(vraag: str, evaluatieset):
    persona_context = maak_persona_context(evaluatieset)
    structured_chat = llm.with_structured_output(ChatAntwoord, method="json_mode")
    chain = chat_prompt | structured_chat
    return chain.invoke({"persona_context": persona_context, "vraag": vraag})

# ---------------- SIDEBAR ----------------
st.sidebar.title("Instellingen")
temp = st.sidebar.slider("Temperature", 0.0, 1.0, 0.5, 0.1)

opdracht = st.sidebar.text_area(
    "Persona-opdracht",
    value="""Genereer de volgende synthetische UX-personas voor een digitaal zorgplatform:
- 3 reumapatienten gevarieerd in leeftijd, achtergrond en digitale vaardigheid
- 1 zorgpersoneel verpleegkundige of arts
- 1 UX designer gespecialiseerd in inclusief ontwerp

Maak elke persona realistisch en specifiek. Vermijd stereotypen. Zorg voor diversiteit in leeftijd, geslacht, culturele achtergrond en digitale vaardigheid.""",
    height=220
)

if "persona_data" not in st.session_state:
    st.session_state.persona_data = None

if "evaluatieset" not in st.session_state:
    st.session_state.evaluatieset = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- UI ----------------
st.title("Persona Chatbot")
st.write("Genereer personas, valideer ze op bias en chat vervolgens vanuit hun perspectief.")

col1, col2 = st.columns(2)

with col1:
    if st.button("Genereer personas"):
        with st.spinner("Personas genereren..."):
            llm.temperature = temp
            resultaat = genereer_personas(opdracht)
            st.session_state.persona_data = resultaat

            evaluatieset = [(p.naam, persona_naar_tekst(p)) for p in resultaat.personas]
            st.session_state.evaluatieset = evaluatieset

        st.success(f"{len(resultaat.personas)} personas gegenereerd")

with col2:
    if st.button("Valideer personas"):
        if st.session_state.evaluatieset is None:
            st.warning("Genereer eerst personas.")
        else:
            with st.spinner("Valideren..."):
                resultaten = []
                for naam, tekst in st.session_state.evaluatieset:
                    schema = valideer_persona(tekst)
                    resultaten.append(schema)
                st.session_state.validatieresultaten = resultaten
            st.success("Validatie klaar")

# ---------------- RESULTATEN ----------------
if st.session_state.persona_data:
    st.subheader("Gegenereerde personas")
    for p in st.session_state.persona_data.personas:
        with st.expander(f"{p.naam} — {p.doelgroep}"):
            st.write(f"**Leeftijd:** {p.leeftijd}")
            st.write(f"**Achtergrond:** {p.achtergrond}")
            st.write("**Uitdagingen:**")
            st.write(p.uitdagingen)
            st.write("**Gedrag:**")
            st.write(p.gedrag)

if "validatieresultaten" in st.session_state:
    st.subheader("Validatieresultaten")
    for r in st.session_state.validatieresultaten:
        st.markdown(f"### {r.naam}")
        st.write(f"Bias: {r.bias.score} ({kleur_label(r.bias.score)}) — {r.bias.toelichting}")
        st.write(f"Hallucinaties: {r.hallucinaties.score} ({kleur_label(r.hallucinaties.score)}) — {r.hallucinaties.toelichting}")
        st.write(f"Inclusie: {r.inclusie.score} ({kleur_label(r.inclusie.score)}) — {r.inclusie.toelichting}")
        st.write(f"Totaalscore: {r.totaalscore} ({kleur_label(r.totaalscore)})")

# ---------------- CHAT ----------------
st.divider()
st.subheader("Chat met de personas")

if st.session_state.messages:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

prompt = st.chat_input("Stel een vraag aan de personas...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.evaluatieset is None:
        antwoord = "Genereer eerst personas zodat ik vanuit hun perspectief kan antwoorden."
        persona_naam = "Systeem"
        uitleg = "Er is nog geen persona-context beschikbaar."
    else:
        with st.spinner("Antwoord genereren..."):
            resultaat = chatbot_vraag(prompt, st.session_state.evaluatieset)
            persona_naam = resultaat.persona_naam
            antwoord = resultaat.antwoord
            uitleg = resultaat.uitleg

    output = f"**{persona_naam}**\n\n{antwoord}\n\n*Kies reden: {uitleg}*"
    st.session_state.messages.append({"role": "assistant", "content": output})

    with st.chat_message("assistant"):
        st.markdown(output)



