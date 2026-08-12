# 🧬 MolPredict EGFR API

Backend REST desarrollado con **FastAPI + RDKit** para el procesamiento molecular de la plataforma **MolPredict EGFR**.

🌐 **Frontend:** [MolPredict EGFR](https://mol-insight-studio.lovable.app)

💻 **Repositorio frontend:** [molpredict-egfr](https://github.com/ibanezmariela78-lab/molpredict-egfr)

---

## 🔬 Sobre la API

Esta API proporciona los servicios de procesamiento molecular utilizados por MolPredict EGFR.

Permite validar estructuras químicas en formato **SMILES**, calcular descriptores fisicoquímicos mediante **RDKit**, generar representaciones moleculares 2D y realizar búsquedas de similitud estructural.

También incluye una predicción demostrativa de actividad frente a EGFR.

> La predicción pIC50/IC50 es demostrativa y no corresponde actualmente a un modelo QSAR científicamente validado.

---

## ⚙️ Tecnologías

* Python
* FastAPI
* RDKit
* Uvicorn
* Pydantic
* REST API
* Replit
* GitHub

---

## 🚀 Endpoints principales

### Estado del servicio

```http
GET /health
```

Permite comprobar que la API está disponible y que RDKit se encuentra operativo.

---

### Validación molecular

```http
POST /api/v1/molecules/validate
```

Valida y canonicaliza una estructura química en formato SMILES.

---

### Descriptores fisicoquímicos

```http
POST /api/v1/molecules/descriptors
```

Calcula propiedades moleculares mediante RDKit, entre ellas:

* Peso molecular
* LogP
* TPSA
* Donantes de H
* Aceptores de H
* Enlaces rotables
* Anillos aromáticos
* Fracción Csp3
* Reglas orientativas de Lipinski

---

### Representación molecular 2D

```http
POST /api/v1/molecules/render
```

Genera una representación 2D de la molécula a partir del SMILES utilizando RDKit.

---

### Predicción EGFR

```http
POST /api/v1/predictions/egfr
```

Devuelve una predicción demostrativa de:

* pIC50
* IC50
* nivel de actividad
* confianza
* dominio de aplicabilidad
* factores favorables
* factores desfavorables

---

### Similitud molecular

```http
POST /api/v1/similarity/search
```

Busca moléculas estructuralmente similares utilizando fingerprints moleculares y similitud de Tanimoto.

---

## 📚 Documentación interactiva

FastAPI genera automáticamente documentación OpenAPI.

Una vez desplegada la API se puede consultar mediante:

```text
/docs
```

La documentación permite visualizar los endpoints, contratos de entrada y salida y ejecutar pruebas directamente desde el navegador.

---

## 🏗️ Arquitectura

```text
MolPredict Frontend
        │
        │ HTTPS / REST
        ▼
     FastAPI
        │
        ▼
      RDKit
        │
        ├── Validación SMILES
        ├── Canonicalización
        ├── Descriptores moleculares
        ├── Renderizado 2D
        └── Similitud estructural
        │
        ▼
Predicción EGFR demostrativa
```

---

## 🔗 Integración con el frontend

El frontend React consume esta API para realizar el procesamiento molecular.

Flujo simplificado:

```text
Usuario ingresa SMILES
        ↓
Frontend React
        ↓
FastAPI
        ↓
RDKit
        ↓
Resultados moleculares
        ↓
Visualización en MolPredict
```

---

## ⚠️ Disclaimer científico

MolPredict EGFR es un proyecto experimental y educativo de portfolio.

Los cálculos moleculares se realizan mediante RDKit.

La predicción pIC50/IC50 actualmente es **demostrativa y no está científicamente validada**.

Los resultados no deben utilizarse para decisiones clínicas, regulatorias ni experimentales y no reemplazan ensayos químicos, biológicos, toxicológicos, preclínicos o clínicos.

---

## 🎯 Objetivo

Este backend forma parte de un proyecto interdisciplinario que integra:

* Química medicinal
* Quimioinformática
* Ciencia de datos
* Desarrollo de APIs
* Procesamiento molecular
* Inteligencia artificial
* Desarrollo web científico

---

## 👩‍💻 Autora

**Mariela Ibáñez**

Química · Ciencia de Datos · Inteligencia Artificial · Quimioinformática

🌐 [MolPredict EGFR](https://mol-insight-studio.lovable.app)
💻 [GitHub](https://github.com/ibanezmariela78-lab)
💼 [LinkedIn](https://www.linkedin.com/in/mariela-ibanez-quimioinformatica/)
