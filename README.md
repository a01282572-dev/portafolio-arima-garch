# Portafolio S&P 500: ARIMA intradía, regresión, datos de panel y GARCH

Proyecto de Programación y Modelación Financiera (Maestría en Finanzas).
Autora: Fernanda Enríquez.

## Contenido

| Archivo | Qué es |
|---|---|
| `Proyecto_Portafolio_ARIMA_GARCH.Rmd` | Documento principal de RStudio. Se compila a **HTML** y a **Word**. |
| `Proyecto_Portafolio_ARIMA_GARCH.ipynb` | El mismo código como notebook de R para **Google Colab**. |
| `extraer_refinitiv.py` | Descarga todos los datos desde **LSEG Workspace (Refinitiv)**. |
| `PROMPT_POSIT_ASSISTANT.md` | Prompt para Posit Assistant, el asistente de IA integrado en RStudio. |
| `data/` | Carpeta donde se guardan los CSV de Refinitiv. |

**Acciones:** STX, VLO, DGX, NUE y CPAY (selección para ARIMA y portafolio) + AAPL, MSFT, JPM, KO y XOM (control, de la actividad de clase).
**Capital:** USD 943,990.81.

## 1. Extraer los datos de Refinitiv (LSEG Workspace)

1. Abre **LSEG Workspace** en tu computadora e inicia sesión. Debe quedarse abierto.
2. (Si la API lo pide) En la barra de búsqueda de Workspace escribe `APPKEY`, genera una App Key con la casilla **EDP API** y cópiala.
3. En la terminal, dentro de esta carpeta:
   ```bash
   pip install lseg-data pandas
   # Windows (PowerShell):  $env:LSEG_APP_KEY="tu_app_key"
   # Mac/Linux:             export LSEG_APP_KEY="tu_app_key"
   python extraer_refinitiv.py
   ```
4. Se crean `data/diario/*.csv`, `data/intradia/*_5min.csv`, `data/intradia/*_60min.csv` y `data/fundamentales_trimestrales.csv`.

**Sin Python (manual):** busca el RIC (por ejemplo `STX.OQ`) → app **Price History** → intervalo *5 Minutes* / *1 Hour* / *Daily* → **Export to Excel** → guarda como CSV con las columnas `Date, Open, High, Low, Close, Volume`. Para los fundamentales usa **Financials** con frecuencia *Quarterly*, o el complemento de Excel con **Build Formula**. Los códigos de campo vienen en la sección 3 del Rmd.

> Si exportas desde Excel, revisa la zona horaria de las fechas y ajusta `TZ_ARCHIVO` en el Rmd (por ejemplo `"America/Mexico_City"`).

## 2. Compilar en RStudio (HTML + Word)

```r
rmarkdown::render("Proyecto_Portafolio_ARIMA_GARCH.Rmd", output_format = "all")
```

También puedes usar el botón **Knit** y elegir *Knit to HTML* o *Knit to Word*. Para tener **PDF**, abre el Word y usa *Guardar como PDF*.

Si todavía no tienes los CSV de Refinitiv, el documento usa Yahoo Finance para los precios diarios. Las secciones de ARIMA intradía y de panel se saltan solas hasta que existan los archivos.

## 3. Subir a GitHub

```bash
git init
git add .
git commit -m "Proyecto portafolio ARIMA/GARCH"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/portafolio-arima-garch.git
git push -u origin main
```

O desde la web: **New repository** → **uploading an existing file** → arrastra los archivos.

## 4. Abrir en Google Colab (link para entregar)

1. Entra a <https://colab.research.google.com> → **File → Open notebook → GitHub** → pega la URL de tu repositorio → abre `Proyecto_Portafolio_ARIMA_GARCH.ipynb`.
   Otra forma es **File → Upload notebook** con el `.ipynb`.
2. **Runtime → Change runtime type → R**.
3. La primera celda clona tu repositorio para tener la carpeta `data/`. Cambia `TU_USUARIO` por tu usuario.
4. **File → Save a copy in Drive** → botón **Share** → *Cualquier persona con el enlace* → copia el link de Drive.

> La API de Refinitiv solo funciona en la computadora donde está abierto Workspace. Por eso los datos se descargan localmente, se suben a GitHub y Colab los lee de ahí.

---
*Trabajo académico. No es recomendación de inversión.*
