import argparse
import sys
from datetime import date
from helpers.utils import limpiar_consola
from services.importar_partes import importar_partes_trabajo
from services.informe_lems import (
  generar_informe_actividad_de_lems_y_gtres
)

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "--anyos",
    type=int,
    nargs="+",
    default=[date.today().year],
    metavar="AÑO",
    help="Año o años para los que generar el informe.",
  )
  args = parser.parse_args()

  limpiar_consola()
  importar_partes_trabajo()
  for anyo in args.anyos:
    generar_informe_actividad_de_lems_y_gtres(anyo)

if __name__ == "__main__":
  main()
