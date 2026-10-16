from pathlib import Path


BASE_PROYECTO = Path(__file__).resolve().parents[2]
CARPETA_PARTES = BASE_PROYECTO / "partes"
DB_PARTES = BASE_PROYECTO / "partes.db"
DIAS_SEMANA = ("L", "M", "X", "J", "V", "S", "D")
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
