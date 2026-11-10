# Prompt para Posit Assistant (asistente integrado de RStudio)


```
Eres mi asistente de análisis financiero en R. Estoy en la Maestría en Finanzas y mi
proyecto es Proyecto_Portafolio_ARIMA_GARCH.Rmd, que está abierto en el editor.
Revisa el archivo, la carpeta data/ y mi sesión de R antes de proponer cambios.

CONTEXTO
- Capital: USD 943,990.81.
- Acciones de selección (no típicas del S&P 500): STX, VLO, DGX, NUE, CPAY.
- Acciones de control (actividad de clase): AAPL, MSFT, JPM, KO, XOM.
- Los datos vienen de LSEG Workspace (Refinitiv), exportados desde Excel a CSV en la
  carpeta definida por RUTA_DATOS (por defecto "data"):
  data/diario/<TICKER>.csv y data/diario/<factor>.csv (mercado, vix, tasa10, petroleo, dolar),
  data/intradia/<TICKER>_5min.csv y _60min.csv, data/fundamentales_trimestrales.csv.
  Columnas de precios: Date, Open, High, Low, Close, Volume.
- Las horas intradía están en hora de Ciudad de México (TZ_ARCHIVO = "America/Mexico_City")
  y marcan el CIERRE de cada barra (ETIQUETA_BARRA = "fin"). La primera barra de 5 min
  del día debe verse como 09:35 de Nueva York.
- El archivo de fundamentales todavía no trae utilidad_neta, así que el ROE se omite.
  JPM queda fuera del panel porque no tiene CAPEX (es banco).

LO QUE NECESITO
1. Corre el chunk "verificar-archivos" y revisa la tabla de inventario: que estén los
   26 CSV, con las columnas correctas y el rango de fechas esperado. Dime si falta algo
   antes de seguir.
2. Ejecuta el Rmd chunk por chunk, en orden, y detente en cuanto haya un error.
   Explícame la causa y propón la corrección mínima sin cambiar la metodología.
3. Revisa que los modelos estén bien planteados:
   - Regresión simple (CAPM) de las 10 acciones contra el S&P 500.
   - Regresión múltiple (mercado, VIX, tasa a 10 años, Brent, dólar) con VIF,
     Breusch-Pagan, Goldfeld-Quandt, Durbin-Watson y errores robustos HC1.
   - Panel trimestral con plm: pooled, efectos fijos y aleatorios, pFtest, Hausman,
     Wooldridge, Pesaran CD y errores Driscoll-Kraay.
   - ARIMA con barras de 5 minutos y con precios a las 10, 12, 14 y 16 h de Nueva York:
     ADF, KPSS, ACF/PACF, auto.arima con lambda = 0, Ljung-Box, validación fuera de
     muestra contra la caminata aleatoria y pronóstico con intervalos de 80% y 95%.
   - GARCH(1,1) con t de Student y GJR-GARCH (rugarch), volatilidad a 10 días y VaR 95%.
   - Portafolio de Markowitz de máximo Sharpe (pesos entre 10% y 30%), número entero
     de acciones con el capital, backtest con rebalanceo trimestral, estrategia ARIMA
     y estrategia de volatilidad objetivo con GARCH.
4. Con los resultados REALES de mi sesión (no inventes cifras), revisa que las
   interpretaciones automáticas del documento sean correctas y dime cuáles debo ajustar.

REGLAS
- Responde en español y explica cada valor p con una frase sencilla.
- Pídeme permiso antes de editar el Rmd y muéstrame el cambio exacto.
- No borres ni sobrescribas los CSV de data/.
- Usa xts::last() y stats::lag() explícitos (dplyr los enmascara).
- Al final, el documento debe compilar con
  rmarkdown::render("Proyecto_Portafolio_ARIMA_GARCH.Rmd", output_format = "all")
  a HTML y Word sin errores.
```

---

## Prompts de seguimiento (por etapa)


1. **Datos:** `Carga los datos con los chunks hasta "descarga-diaria" y muéstrame una gráfica de los precios base 100 de las 5 acciones de selección contra el S&P 500.`
2. **Intradía:** `Corre el chunk "intradia-carga" y confirma con la tabla de la primera barra del día que TZ_ARCHIVO y ETIQUETA_BARRA están bien (la primera barra de 5 min debe ser 09:35 de Nueva York).`
   **ROE (cuando agregues la utilidad neta):** `Agregué la columna utilidad_neta a data/fundamentales_trimestrales.csv. Verifica que el ROE ya entre al scorecard y al panel, y compara el modelo de panel con y sin ROE.`
3. **Regresiones:** `Ejecuta las secciones de regresión simple y múltiple y resume en una tabla qué acciones son agresivas o defensivas y qué factores son significativos para cada una.`
4. **Panel:** `Ejecuta el panel y explícame paso a paso por qué se eligió ese modelo con las pruebas F, Breusch-Pagan y Hausman.`
5. **ARIMA:** `Revisa los residuales de cada ARIMA. Si alguno no pasa Ljung-Box, prueba un orden alternativo y compara AICc y RMSE fuera de muestra.`
6. **GARCH:** `¿Qué acción tiene la mayor persistencia de volatilidad y hay efecto apalancamiento en alguna? Explícalo con los resultados.`
7. **Portafolio:** `Muéstrame la tabla final de acciones a comprar con el capital y compárala contra la de mínima varianza y la de pesos iguales. STX cayó casi 49% desde el 1 de octubre: ¿cómo cambian los pesos si estimo los rendimientos solo con el CAPM (METODO_MU = "capm")?`
8. **Compilar:** `Compila el documento a HTML y Word y dime si hubo advertencias importantes.`

