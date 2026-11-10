"""
Extrae de LSEG Workspace (antes Refinitiv Workspace / Eikon) los datos que usa
Proyecto_Portafolio_ARIMA_GARCH.Rmd y los guarda en la carpeta data/.

Requisitos:
  1. LSEG Workspace abierto y con sesión iniciada en la misma computadora.
  2. pip install lseg-data pandas
  3. (Si lo pide) una App Key: en Workspace busca "APPKEY", genera una
     con la casilla "EDP API" y ponla en la variable APP_KEY de abajo.

Uso:
  python extraer_refinitiv.py
"""

import os
import time
from datetime import datetime, timedelta

import pandas as pd
import lseg.data as ld

APP_KEY = os.environ.get("LSEG_APP_KEY", "")  # o pega aquí tu App Key

ACCIONES = {
    "STX": "STX.OQ", "VLO": "VLO.N", "DGX": "DGX.N", "NUE": "NUE.N", "CPAY": "CPAY.N",
    "AAPL": "AAPL.OQ", "MSFT": "MSFT.OQ", "JPM": "JPM.N", "KO": "KO.N", "XOM": "XOM.N",
}
SELECCION = ["STX", "VLO", "DGX", "NUE", "CPAY"]          # las que llevan ARIMA intradía
FACTORES = {"mercado": ".SPX", "vix": ".VIX", "tasa10": "US10YT=RR",
            "petroleo": "LCOc1", "dolar": ".DXY"}

INICIO_DIARIO = "2019-11-29"
HOY = datetime.utcnow()
DIAS_5MIN = 90      # LSEG conserva un historial limitado de barras intradía;
DIAS_60MIN = 365    # si pides más de lo disponible, simplemente devuelve menos.

# Campos candidatos para el precio de cierre (acciones, índices, bonos, futuros)
CAMPOS_CIERRE = ["TRDPRC_1", "B_YLD_1", "SETTLE", "MID_PRICE", "CLOSE", "BID"]

# Campos fundamentales trimestrales (verifícalos en Data Item Browser - DIB)
CAMPOS_FUND = {
    "TR.F.TotRevenue.periodenddate": "fecha",
    "TR.F.TotRevenue": "ingresos",
    "TR.F.OpProfBefNonRecurIncExpn": "utilidad_operativa",
    "TR.F.NetIncAfterMinInt": "utilidad_neta",
    "TR.F.ShHoldEqParentShHoldTot": "capital_contable",
    "TR.F.DebtTot": "deuda_total",
    "TR.F.NetCashFlowOp": "flujo_operativo",
    "TR.F.CAPEXTot": "capex",
}

os.makedirs("data/diario", exist_ok=True)
os.makedirs("data/intradia", exist_ok=True)


def a_formato_estandar(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte la salida de get_history a Date, Open, High, Low, Close, Volume."""
    df = df.copy()
    df.columns = [str(c).upper() for c in df.columns]
    cierre = next((c for c in CAMPOS_CIERRE if c in df.columns and df[c].notna().any()), None)
    if cierre is None:
        raise ValueError(f"No encontré columna de cierre en: {list(df.columns)}")
    salida = pd.DataFrame(index=df.index)
    salida["Open"] = df.get("OPEN_PRC")
    salida["High"] = df.get("HIGH_1")
    salida["Low"] = df.get("LOW_1")
    salida["Close"] = df[cierre]
    salida["Volume"] = df.get("ACVOL_UNS")
    salida.index.name = "Date"
    return salida.dropna(subset=["Close"])


def historia(ric: str, intervalo: str, inicio: datetime, fin: datetime, ventana_dias: int) -> pd.DataFrame:
    """Descarga por ventanas para no rebasar el límite de filas por solicitud."""
    partes, t0 = [], inicio
    while t0 < fin:
        t1 = min(t0 + timedelta(days=ventana_dias), fin)
        try:
            df = ld.get_history(universe=ric, interval=intervalo,
                                start=t0.strftime("%Y-%m-%dT%H:%M:%S"),
                                end=t1.strftime("%Y-%m-%dT%H:%M:%S"))
            if df is not None and len(df):
                partes.append(df)
        except Exception as e:  # noqa: BLE001
            print(f"   aviso {ric} {intervalo} {t0:%Y-%m-%d}: {e}")
        t0 = t1
        time.sleep(0.3)
    if not partes:
        raise ValueError(f"Sin datos para {ric} ({intervalo})")
    df = pd.concat(partes)
    return df[~df.index.duplicated(keep="last")].sort_index()


def main():
    if APP_KEY:
        ld.open_session(name="desktop.workspace", app_key=APP_KEY)
    else:
        ld.open_session()
    print("Sesión abierta con LSEG Workspace")

    inicio_d = datetime.strptime(INICIO_DIARIO, "%Y-%m-%d")

    # 1) Precios diarios de acciones y factores
    for nombre, ric in {**ACCIONES, **FACTORES}.items():
        print(f"Diario  {nombre:9s} {ric}")
        df = historia(ric, "daily", inicio_d, HOY, 3650)
        a_formato_estandar(df).to_csv(f"data/diario/{nombre}.csv")

    # 2) Intradía de las 5 acciones seleccionadas (marcas de tiempo en UTC)
    for t in SELECCION:
        ric = ACCIONES[t]
        print(f"5 min   {t:9s} {ric}")
        df = historia(ric, "5min", HOY - timedelta(days=DIAS_5MIN), HOY, 20)
        a_formato_estandar(df).to_csv(f"data/intradia/{t}_5min.csv")
        print(f"60 min  {t:9s} {ric}")
        df = historia(ric, "60min", HOY - timedelta(days=DIAS_60MIN), HOY, 90)
        a_formato_estandar(df).to_csv(f"data/intradia/{t}_60min.csv")

    # 3) Fundamentales trimestrales (últimos 20 trimestres, millones de USD)
    print("Fundamentales trimestrales")
    fund = ld.get_data(universe=list(ACCIONES.values()), fields=list(CAMPOS_FUND.keys()),
                       parameters={"SDate": "0", "EDate": "-19", "Period": "FQ0",
                                   "Frq": "FQ", "Scale": "6", "Curn": "USD"})
    fund.columns = ["ric"] + list(CAMPOS_FUND.values())
    inverso = {v: k for k, v in ACCIONES.items()}
    fund.insert(0, "ticker", fund["ric"].map(inverso))
    fund["fecha"] = pd.to_datetime(fund["fecha"]).dt.date
    fund = fund.dropna(subset=["fecha", "ingresos"]).drop(columns="ric")
    fund.to_csv("data/fundamentales_trimestrales.csv", index=False)
    print(fund.groupby("ticker").size())

    ld.close_session()
    print("Listo. Archivos en la carpeta data/")


if __name__ == "__main__":
    main()
