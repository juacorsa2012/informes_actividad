import sys
import os
import sqlite3
from pathlib import Path
from helpers.constantes import DB_PARTES, CARPETA_PARTES
from helpers.utils import obtener_partes_trabajo, extraer_datos_parte, extraer_informacion_fecha, normalizar_desplazamiento

BASE = Path(__file__).resolve().parents[2] 
FICHERO_DESPLAZAMIENTO_CLIENTES = BASE / "desplazamiento_clientes.txt"
FICHERO_PARTES_CON_VARIOS_TECNICOS = BASE / "partes_detectados_con_varios_tecnicos.txt"

def vaciar_tabla_partes_temp(conn: sqlite3.Connection) -> None:
  conn.execute("DELETE FROM partes_temp")  

def mostrar_barra_progreso(actual: int, total: int, nombre_archivo: str = "", ancho: int = 50):
  porcentaje = actual / total
  bloques_completos = int(ancho * porcentaje)
  barra = "[" + "#" * bloques_completos + " " * (ancho - bloques_completos) + "]"   
  porcentaje_texto = f"{porcentaje * 100:.1f}%"    
  
  longitud_nombre = 40
  if len(nombre_archivo) > longitud_nombre:
    nombre_archivo = nombre_archivo[:longitud_nombre-3] + "..."
    
  sys.stdout.write(f"\r{barra} {porcentaje_texto} ({actual}/{total}) {nombre_archivo:<43}")
  sys.stdout.flush()
    
  if actual == total:
    print()  


def insertar_parte(
  conn: sqlite3.Connection,
  numero: int,
  fecha: str,
  cliente: str,
  tecnico: str,
  minutos: int,
  desplazamiento: str,
  tecnicos: int,
  mes: int,
  año: int,
  trimestre: int,
  dia_semana: str,
  duracion_total: int,
  minutos_desplazamiento: int
) -> None:
    conn.execute(
      """
      INSERT INTO partes_temp (
        numero,
        fecha,
        cliente,
        tecnico,
        minutos,
        desplazamiento,
        tecnicos,
        mes,
        año,
        trimestre,
        dia_semana,
        duracion_total,
        minutos_desplazamiento
      )
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      """,
        (
          numero,
          fecha,
          cliente,
          tecnico,
          minutos,
          desplazamiento,
          tecnicos,
          mes,
          año,
          trimestre,
          dia_semana,
          duracion_total,
          minutos_desplazamiento
        ),
    )

def obtener_partes_con_mas_de_un_tecnico(conn: sqlite3.Connection) -> list[sqlite3.Row]:  
  query = """
    SELECT numero, fecha, cliente, tecnico, minutos, desplazamiento 
    FROM partes_temp 
    WHERE tecnicos > 1
    ORDER BY numero
  """
  return conn.execute(query).fetchall()

def resolver_desplazamientos(conn: sqlite3.Connection) -> None:
  desplazamientos_clientes: list[tuple[str, int]] = []

  if not os.path.exists(FICHERO_DESPLAZAMIENTO_CLIENTES):
    print(f"Aviso: no existe el fichero {FICHERO_DESPLAZAMIENTO_CLIENTES}.")
  else:
    with open(FICHERO_DESPLAZAMIENTO_CLIENTES, "r", encoding="utf-8") as archivo:
      for numero_linea, linea in enumerate(archivo, start=1):
        linea = linea.strip()
        if not linea:
          continue

        partes = linea.split(":")
        if len(partes) != 2 or not partes[0].strip():
          raise ValueError(
            f"{FICHERO_DESPLAZAMIENTO_CLIENTES}, línea {numero_linea}: "
            f"formato inválido; se esperaba CLIENTE:minutos ({linea!r})."
          )

        try:
          minutos = int(partes[1].strip())
        except ValueError as e:
          raise ValueError(
            f"{FICHERO_DESPLAZAMIENTO_CLIENTES}, línea {numero_linea}: "
            f"minutos no enteros ({partes[1].strip()!r})."
          ) from e

        if minutos < 0:
          raise ValueError(
            f"{FICHERO_DESPLAZAMIENTO_CLIENTES}, línea {numero_linea}: "
            f"los minutos no pueden ser negativos ({minutos})."
          )

        desplazamientos_clientes.append((partes[0].strip().upper(), minutos))

  conn.execute(""" UPDATE partes_temp SET minutos_desplazamiento = 0 """)
  conn.execute(""" UPDATE partes_temp SET minutos_desplazamiento = 30 WHERE desplazamiento = 'SI' """)

  for cliente, minutos in desplazamientos_clientes:
    conn.execute(
      "UPDATE partes_temp SET minutos_desplazamiento = ? WHERE cliente = ? AND desplazamiento = 'SI'",
      (minutos, cliente),
    )

def resolver_duracion_total(conn: sqlite3.Connection) -> None:
  conn.execute(""" UPDATE partes_temp SET duracion_total = minutos + minutos_desplazamiento """)

def limpiar_partes_existentes(conn: sqlite3.Connection) -> None:
  conn.execute("DELETE FROM partes WHERE numero IN (SELECT numero FROM partes_temp)")    
  
def volcar_partes(conn: sqlite3.Connection) -> None:
  limpiar_partes_existentes(conn)
  conn.execute("""
    INSERT INTO partes (numero, fecha, cliente, tecnico, minutos, desplazamiento, duracion_total, mes, año, trimestre, dia_semana)
    SELECT numero, fecha, cliente, tecnico, minutos, minutos_desplazamiento, duracion_total, mes, año, trimestre, dia_semana
    FROM partes_temp
  """)

def importar_partes_trabajo() -> None:  
  archivos = obtener_partes_trabajo()
  if not archivos:  
    return

  print("Importando partes de trabajo...")
  with sqlite3.connect(DB_PARTES) as conn:
    vaciar_tabla_partes_temp(conn)
    errores: list[str] = []
    
    for i, archivo in enumerate(archivos, 1): 
      # mostrar_barra_progreso(i, len(archivos), archivo)       
      datos = extraer_datos_parte(fichero=os.path.join(CARPETA_PARTES, archivo))
      
      if datos is None:
        errores.append(archivo)
        continue

      try:
        info_fecha = extraer_informacion_fecha(datos["fecha"])
      except ValueError as e:
        print(f"\nFecha inválida en {archivo}: {e}")
        errores.append(archivo)
        continue
        
      insertar_parte(
        conn,
        numero=datos["numero_parte"],
        fecha=datos["fecha"],
        cliente=datos["cliente"].upper(),
        tecnico=datos["tecnico"].upper(),        
        minutos=round(datos["horas"] * 60),     
        desplazamiento=normalizar_desplazamiento(datos["desplazamiento"]),
        tecnicos=datos["tecnicos"],
        mes=int(info_fecha["mes"]),
        año=int(info_fecha["año"]),
        trimestre=int(info_fecha["trimestre"]),
        dia_semana=info_fecha["dia_semana"],
        duracion_total=0,
        minutos_desplazamiento=0
      )    

    if errores:
      print(f"\n{len(errores)} fichero(s) no procesados: {', '.join(errores)}")

    partes = obtener_partes_con_mas_de_un_tecnico(conn)
    if partes:        
      print(f"¡Atención! Se han detectado {len(partes)} parte(s) de trabajo con más de un técnico.")
      print(f"Ver fichero {FICHERO_PARTES_CON_VARIOS_TECNICOS} para resolver esta situación.")

      with open(FICHERO_PARTES_CON_VARIOS_TECNICOS, "w", encoding="utf-8") as archivo:
        for parte in partes:
          archivo.write(":".join(str(c) for c in parte[:6]) + "\n")
    else:
      try:
        resolver_desplazamientos(conn)
      except ValueError as e:
        vaciar_tabla_partes_temp(conn)
        print(f"\nImportación cancelada: {e}")
      else:
        resolver_duracion_total(conn)
        volcar_partes(conn)
