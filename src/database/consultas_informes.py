import sqlite3

def contar_numero_partes_por_anyo(conn: sqlite3.Connection, año: int, mes: int) -> int:
  query = "SELECT COUNT(DISTINCT numero) FROM partes WHERE año = ? AND mes = ?"
  resultado = conn.execute(query, (año, mes,)).fetchone()
  return resultado[0]

def contar_minutos_partes_por_anyo_mes(conn: sqlite3.Connection, año: int, mes: int) -> int:
  query = "SELECT COALESCE(SUM(duracion_total), 0) FROM partes WHERE año = ? AND mes = ?"
  resultado = conn.execute(query, (año, mes,)).fetchone()
  return resultado[0]

def contar_partes_por_anyo_dia_semana(conn: sqlite3.Connection, año: int, dia: str) -> int:
  query = "SELECT COUNT(*) FROM partes WHERE año = ? AND dia_semana = ?"
  resultado = conn.execute(query, (año, dia,)).fetchone()
  return resultado[0]



