import re
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, TypedDict
from helpers.constantes import CARPETA_PARTES, DIAS_SEMANA

class InfoFecha(TypedDict):
  mes: int
  año: int
  trimestre: int
  dia_semana: str

class DatosParte(TypedDict):
  cliente: str
  numero_parte: int
  fecha: str
  horas: float
  desplazamiento: str
  tecnico: str
  informe: str
  tecnicos: int


def obtener_partes_trabajo() -> list[str]:
  carpeta = Path(CARPETA_PARTES)
  if not carpeta.is_dir():
    raise FileNotFoundError(f"No existe la carpeta de partes: {carpeta}")

  return sorted(
    f.name for f in carpeta.iterdir()
    if f.is_file() and f.suffix.lower() == ".txt"
  )

def existe_carpeta_partes() -> bool:
  carpeta = Path(CARPETA_PARTES)

  if not carpeta.is_dir():
    print(f"No existe la carpeta de partes: {carpeta}")
    return False

  return True

def limpiar_consola() -> None:
  if shutil.which("clear"):
    subprocess.run(["clear"])
  else:
    subprocess.run("cls", shell=True)

def extraer_informacion_fecha(fecha: str) -> InfoFecha:
  fecha_dt = datetime.strptime(fecha.strip(), "%Y-%m-%d")

  return {
    "mes": fecha_dt.month,
    "año": fecha_dt.year,
    "trimestre": (fecha_dt.month - 1) // 3 + 1,
    "dia_semana": DIAS_SEMANA[fecha_dt.weekday()],
  }

def extraer_datos_parte(fichero: str) -> Optional[DatosParte]:
  try:
    with open(fichero, "r", encoding="utf-8") as archivo:
      texto = archivo.read()
      numero_parte = re.search(r"Nº de Parte:\s*(\d+)", texto).group(1)      
      fecha = re.search(r"Fecha:\s*([\d\- ]+)", texto).group(1)
      fecha = fecha.replace(" ", "").strip()
      tecnico_match = re.search(r"Técnico:\s*(.+)", texto)
      tecnico = tecnico_match.group(1).strip() if tecnico_match else ""
      cliente_match = re.search(r"Cliente:\s*(.+?)\n\s*Horas:", texto, re.DOTALL)
      cliente = cliente_match.group(1).replace("\n", " ").strip() if cliente_match else ""     

      #horas = float(re.search(r"Horas:\s*([\d\.]+)", texto).group(1))
      horas_texto = re.search(r"Horas:\s*(\d+(?:[.,]\d+)?)", texto).group(1)
      horas = float(horas_texto.replace(",", "."))            
      
      informe_match = re.search(r"Informe:\s*(.+?)\n\s*Componentes:", texto, re.DOTALL)
      informe = informe_match.group(1).replace("\n", " ").strip() if informe_match else ""
      tecnicos = int(re.search(r"Nº de Técnicos:\s*(\d+)", texto).group(1))
      desplazamiento = re.search(r"Desplazamiento:\s*(\w+)", texto).group(1)

      return {
        "cliente": cliente.upper(),
        "numero_parte": int(numero_parte),
        "fecha": fecha,
        "horas": horas,
        "desplazamiento": desplazamiento,
        "tecnico": tecnico.upper(),          
        "informe": informe,
        "tecnicos": tecnicos,      
      }  
  
  except FileNotFoundError:
    print(f"\nArchivo no encontrado: {fichero}")
    return None
  
  except AttributeError as e:
    print(f"\nNo se encontró un campo requerido en {fichero}: {str(e)}")
    return None  
    
  except Exception as e:
    print(f"\nEl fichero {fichero} no se ha procesado: {str(e)}")
    return None

def normalizar_desplazamiento(valor: str) -> str:
  return valor.strip().upper().replace("Í", "I") 

def minutos_a_horas(minutos: int) -> int:
  return round(minutos / 60)
