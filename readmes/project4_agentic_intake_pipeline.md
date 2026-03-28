<!-- Copied from project-readmes/examples/project4_readme.md -->
# Agentic Clinical Intake Pipeline

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-purple)
![FHIR R4](https://img.shields.io/badge/FHIR-R4-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

A multi-step agentic pipeline that ingests unstructured clinical notes, extracts structured data via specialized LLM agents, validates against clinical schemas, and writes FHIR R4-compliant resources to the EHR.

**Key Results:** Demographics F1=0.975, Medications F1=0.93, 97.5% FHIR schema valid, 35% auto-approve rate

**Key Tech:** LangGraph, parallel extraction agents, FHIR R4, human-in-the-loop checkpoints

[Full README](https://github.com/kavoshm/clinical-intake-pipeline)
