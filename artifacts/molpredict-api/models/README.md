# Directorio de Modelos — MolPredict EGFR

Este directorio está reservado para los archivos del modelo QSAR una vez que sea entrenado y validado.

## Estado actual

| Campo              | Valor                    |
|--------------------|--------------------------|
| **Estado**         | No entrenado             |
| **Versión**        | qsar-demo-v0.1           |
| **Tarea**          | Regresión (pIC50)        |
| **Target**         | EGFR (Epidermal Growth Factor Receptor) |
| **Validado**       | No                       |

## Archivos esperados (futuro)

```
models/
  qsar_egfr_v1.joblib        # Modelo entrenado (scikit-learn / ensemble)
  feature_scaler.joblib      # Normalizador de descriptores
  feature_names.json         # Lista de descriptores usados en el entrenamiento
  training_metrics.json      # Métricas de entrenamiento y validación cruzada
  ad_train_fps.npy           # Fingerprints del set de entrenamiento (dominio de aplicabilidad)
  README_model.md            # Documentación del modelo
```

## Roadmap

1. **Recolección de datos** — Descargar actividades EGFR de ChEMBL (IC50, pIC50 experimentales).
2. **Curaduría** — Filtrar duplicados, estandarizar SMILES, eliminar datos ambiguos.
3. **Ingeniería de características** — Morgan FP + descriptores RDKit.
4. **Entrenamiento** — Random Forest / Gradient Boosting con validación cruzada.
5. **Validación** — Set de prueba externo, métricas R², RMSE, Q².
6. **Dominio de aplicabilidad** — Definir límites usando similitud sobre el set de entrenamiento.
7. **Despliegue** — Reemplazar la lógica demo con el modelo real usando joblib.

## Disclaimer científico

Las predicciones actuales son **demostrativas**. No están basadas en datos experimentales
verificados ni en un modelo estadístico validado. No deben usarse para tomar decisiones
científicas, clínicas ni regulatorias.
