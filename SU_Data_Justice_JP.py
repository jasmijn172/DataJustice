import os
import json
import csv
import io
import streamlit as st
from typing import TypedDict, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

# ============================================================
# TITEL & API KEY
# ============================================================

st.title("Bias‑Justice Validator & Persona Generator")

api_key = st.text_input("Voer je GROQ API key in", type="password")

if not api_key:
    st.warning("Voer eerst je API‑key in om verder te gaan.")
    st.stop()

os.environ["GROQ_API_KEY"] = api_key
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.8)
st.success("Groq‑verbinding klaar")


# ============================================================
# SCHEMA'S
# ============================================================

class CheckSchema(BaseModel):
    score: int = Field(description="Score van 0 tot 100")
    toelichting: str = Field(description="Maximaal één zin uitleg bij de score")

class PersonaSchema(BaseModel):
    naam: str
    samenvatting: str
    kenmerken: list[str]
    bias: CheckSchema
    hallucinaties: CheckSchema
    inclusie: CheckSchema
    totaalscore: int

st.success("Schema's geladen")


# ============================================================
# VALIDATIE PROMPT
# ============================================================

prompt = ChatPromptTemplate.from_messages([
    ("human", """### Wie ben je
Jij bent een Bias-Justice validator gespecialiseerd in het beoordelen van synthetische UX-persona's.

### De persona
{persona}

### Output (JSON)
{
  "naam": "...",
  "samenvatting": "...",
  "kenmerken": ["..."],
  "bias":          {"score": 0-100, "toelichting": "..."},
  "hallucinaties": {"score": 0-100, "toelichting": "..."},
  "inclusie":      {"score": 0-100, "toelichting": "..."},
  "totaalscore":   0-100
}
""")
])

st.success("Bias‑Justice prompt geladen")


# ============================================================
# PERSONA GENERATOR
# ============================================================

class GegenereerdePersona(BaseModel):
    naam: str
    doelgroep: str
    leeftijd: int
    achtergrond: str
    uitdagingen: list[str]
    gedrag: list[str]

class PersonaSetSchema(BaseModel):
    personas: list[GegenereerdePersona]

OPDRACHT = """
Genereer de volgende synthetische UX-persona's voor een digitaal zorgplatform:
- 3 reumapatiënten
- 1 zorgpersoneel
- 1 UX designer
"""

genereer_prompt = ChatPromptTemplate.from_messages([
    ("human", """Genereer persona's op basis van deze opdracht:

{opdracht}

Geef ALLEEN JSON terug:
{"personas": [
  {"naam": "...", "doelgroep": "...", "leeftijd": 0,
   "achtergrond": "...", "uitdagingen": ["..."], "gedrag": ["..."]}
]}
""")
])

st.header("Persona Generator")

if st.button("Genereer persona's"):
    with st.spinner("Persona's genereren..."):
        structured_llm = llm.with_structured_output(PersonaSetSchema, method="json_mode")
        chain = genereer_prompt | structured_llm
        resultaat = chain.invoke({"opdracht": OPDRACHT})

        def persona_naar_tekst(p: GegenereerdePersona) -> str:
            uitdagingen = "\n".join(f"- {u}" for u in p.uitdagingen)
            gedrag = "\n".join(f"- {g}" for g in p.gedrag)
            return (
                f"{p.naam}, {p.leeftijd} jaar, {p.doelgroep}\n"
                f"{p.achtergrond}\n\n"
                f"Uitdagingen:\n{uitdagingen}\n\n"
                f"Gedrag:\n{gedrag}"
            )

        evaluatieset = [(p.naam, persona_naar_tekst(p)) for p in resultaat.personas]

        st.session_state["evaluatieset"] = evaluatieset
        st.success(f"{len(evaluatieset)} persona's gegenereerd")

        for naam, tekst in evaluatieset:
            with st.expander(f"Persona: {naam}"):
                st.text(tekst)


# ============================================================
# LANGGRAPH WORKFLOW
# ============================================================

st.header("Bias‑Justice Validatie Workflow")

class PersonaState(TypedDict):
    persona_tekst: str
    persona_schema: Optional[dict]
    validatie_fouten: list
    reparatie_pogingen: int
    export_pad: Optional[str]


def parse_persona(state: PersonaState) -> dict:
    structured_llm = llm.with_structured_output(PersonaSchema, method="json_mode")
    chain = prompt | structured_llm
    response = chain.invoke({"persona": state["persona_tekst"]})
    return {"persona_schema": response.model_dump()}


def valideer_persona(state: PersonaState) -> dict:
    fouten = []
    schema = state["persona_schema"]

    if not schema.get("naam"):
        fouten.append("Naam ontbreekt")
    if not schema.get("samenvatting") or len(schema["samenvatting"]) < 10:
        fouten.append("Samenvatting te kort")
    if not schema.get("kenmerken") or len(schema["kenmerken"]) < 2:
        fouten.append("Minder dan 2 kenmerken")

    for check in ["bias", "hallucinaties", "inclusie"]:
        if not schema.get(check) or schema[check].get("score") is None:
            fouten.append(f"Score ontbreekt voor {check}")
        if not schema.get(check) or not schema[check].get("toelichting"):
            fouten.append(f"Toelichting ontbreekt voor {check}")

    if schema.get("totaalscore") is None:
        fouten.append("Totaalscore ontbreekt")

    return {"validatie_fouten": fouten}


def bepaal_volgende_stap(state: PersonaState) -> str:
    if state["validatie_fouten"] and state["reparatie_pogingen"] < 2:
        return "repareer"
    return "exporteer"


def repareer_persona(state: PersonaState) -> dict:
    pogingen = state["reparatie_pogingen"] + 1

    repareer_prompt = ChatPromptTemplate.from_messages([
        ("human", """Verbeter dit persona-schema:

Schema: {schema}
Fouten: {fouten}
Originele tekst: {persona_tekst}

Geef volledig JSON terug.
""")
    ])

    structured_llm = llm.with_structured_output(PersonaSchema, method="json_mode")
    chain = repareer_prompt | structured_llm
    response = chain.invoke({
        "schema": json.dumps(state["persona_schema"], ensure_ascii=False),
        "fouten": "\n".join(state["validatie_fouten"]),
        "persona_tekst": state["persona_tekst"]
    })

    return {
        "persona_schema": response.model_dump(),
        "reparatie_pogingen": pogingen,
        "validatie_fouten": []
    }


def exporteer_persona(state: PersonaState) -> dict:
    naam = state["persona_schema"]["naam"][:30].replace(" ", "_")
    pad = f"persona_{naam}.json"
    with open(pad, "w", encoding="utf-8") as f:
        json.dump(state["persona_schema"], f, indent=2, ensure_ascii=False)
    return {"export_pad": pad}


workflow = StateGraph(PersonaState)
workflow.add_node("parse", parse_persona)
workflow.add_node("valideer", valideer_persona)
workflow.add_node("repareer", repareer_persona)
workflow.add_node("exporteer", exporteer_persona)

workflow.add_edge(START, "parse")
workflow.add_edge("parse", "valideer")
workflow.add_conditional_edges("valideer", bepaal_volgende_stap,
                               {"repareer": "repareer", "exporteer": "exporteer"})
workflow.add_edge("repareer", "valideer")
workflow.add_edge("exporteer", END)

app = workflow.compile()

st.success("Workflow klaar")


# ============================================================
# WORKFLOW UITVOEREN
# ============================================================

st.subheader("Persona’s valideren")

if "evaluatieset" not in st.session_state:
    st.warning("Genereer eerst persona’s")
else:
    if st.button("Start validatie"):
        personas_output = []

        def kleur_label(score: int) -> str:
            if score <= 70: return "🔴 ROOD"
            if score <= 80: return "🟡 GEEL"
            return "🟢 GROEN"

        for naam, persona in st.session_state["evaluatieset"]:
            st.markdown(f"### {naam}")

            resultaat = app.invoke({
                "persona_tekst": persona,
                "persona_schema": None,
                "validatie_fouten": [],
                "reparatie_pogingen": 0,
                "export_pad": None
            })

            schema = resultaat["persona_schema"]
            schema["reparatie_pogingen"] = resultaat["reparatie_pogingen"]
            personas_output.append(schema)

            st.write(f"**Bias:** {schema['bias']['score']}% {kleur_label(schema['bias']['score'])}")
            st.write(f"**Hallucinaties:** {schema['hallucinaties']['score']}% {kleur_label(schema['hallucinaties']['score'])}")
            st.write(f"**Inclusie:** {schema['inclusie']['score']}% {kleur_label(schema['inclusie']['score'])}")
            st.write(f"**Totaalscore:** {schema['totaalscore']}% {kleur_label(schema['totaalscore'])}")

        st.session_state["personas_output"] = personas_output
        st.success("Validatie compleet!")


# ============================================================
# EXPORT
# ============================================================

st.subheader("Exporteren")

if "personas_output" in st.session_state:
    personas_output = st.session_state["personas_output"]

    # CSV
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow([
        "naam", "samenvatting", "kenmerken",
        "bias_score", "bias_toelichting",
        "hallucinaties_score", "hallucinaties_toelichting",
        "inclusie_score", "inclusie_toelichting",
        "totaalscore", "reparatie_pogingen"
    ])
    for r in personas_output:
        writer.writerow([
            r["naam"],
            r["samenvatting"],
            " | ".join(r["kenmerken"]),
            r["bias"]["score"], r["bias"]["toelichting"],
            r["hallucinaties"]["score"], r["hallucinaties"]["toelichting"],
            r["inclusie"]["score"], r["inclusie"]["toelichting"],
            r["totaalscore"],
            r["reparatie_pogingen"]
        ])

    st.download_button("Download CSV", csv_buffer.getvalue(),
                       file_name="personas_evaluatie.csv", mime="text/csv")

    # JSON
    json_str = json.dumps(personas_output, indent=2, ensure_ascii=False)
    st.download_button("Download JSON", json_str,
                       file_name="personas_evaluatie.json", mime="application/json")
else:
    st.info("Voer eerst de validatie uit.")


# ============================================================
# CHATBOT
# ============================================================

st.header("Chat met een persona")

if "personas_output" not in st.session_state:
    st.warning("Voer eerst de validatie uit")
else:
    personas_output = st.session_state["personas_output"]

    namen = [p["naam"] for p in personas_output]
    keuze = st.selectbox("Kies een persona", namen)

    selected_persona_data = next(p for p in personas_output if p["naam"] == keuze)

    persona_description = f"""
Je bent {selected_persona_data['naam']}.
Samenvatting: {selected_persona_data['samenvatting']}
Kenmerken: {', '.join(selected_persona_data['kenmerken'])}
"""

    chatbot_prompt = ChatPromptTemplate.from_messages([
        ("system", f"Antwoord als deze persona:\n\n{persona_description}"),
        ("human", "{question}")
    ])

    chatbot_chain = chatbot_prompt | llm

    vraag = st.text_input("Stel een vraag aan deze persona")

    if vraag:
        response = chatbot_chain.invoke({"question": vraag})
        st.markdown(f"**{selected_persona_data['naam']}:** {response.content}")



