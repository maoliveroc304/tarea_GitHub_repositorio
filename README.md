# MiniMarket Manager (Streamlit)

Aplicación de prototipo para gestión logística de un minimarket:
- Inventario: CRUD, ajustes de stock, KPIs
- Turnos & Autoevaluación: registro de ingreso/salida y 3 checks (Limpieza, Ordenamiento/llenado de anaqueles, Cuadro de caja chica)
- Dashboard con visualizaciones (Plotly)

## Cómo ejecutar localmente

1. Clona este repositorio o descarga los archivos.
2. Crea un entorno virtual (recomendado) e instala dependencias:
```bash
python -m venv venv
source venv/bin/activate   # o venv\\Scripts\\activate en Windows
pip install -r requirements.txt
```
3. Ejecuta la app:
```bash
streamlit run app.py
```

## Deploy rápido en Streamlit Cloud
1. Sube los archivos a un repositorio en GitHub (ver instrucciones abajo).
2. Conecta tu cuenta de GitHub en https://share.streamlit.io/ y desplega el repo.
3. Streamlit detectará `app.py` y arrancará la app.

## Archivos incluidos
- app.py
- inventory_manager.py
- shifts_manager.py
- requirements.txt
- README.md
