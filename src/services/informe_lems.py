import sqlite3
import matplotlib.pyplot as plt
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader
from reportlab.platypus import PageBreak
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from helpers.constantes import BASE_PROYECTO, DB_PARTES, DIAS_SEMANA, MESES
from helpers.utils import minutos_a_horas
from database.consultas_informes import (
  contar_numero_partes_por_anyo, contar_minutos_partes_por_anyo_mes,
  contar_partes_por_anyo_dia_semana
)


CARPETA_INFORMES_LEMS = BASE_PROYECTO / "informes" / "lems"
ANCHO_UTIL = A4[0] - 4 * cm  # ancho de página menos márgenes de 2 cm

estilos = getSampleStyleSheet()

estilo_titulo = ParagraphStyle(
  "",
  parent=estilos["Title"],
  fontName="Helvetica-Bold",
  fontSize=18,
  textColor=colors.HexColor("#287D5"),
  alignment=TA_CENTER,
  spaceAfter=20,
)

def pie_pagina(canvas, doc):
  canvas.saveState()
  canvas.setFont("Helvetica", 8)
  canvas.setFillColor(colors.grey)
  canvas.drawString(2 * cm, 1.2 * cm, "Informe de actividad de LEMS y GTRES")
  canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
  canvas.restoreState()


def generar_grafico_distribucion_partes_por_meses_y_anyo(conn: sqlite3.Connection, anyo: int) -> Path:   
  partes = [contar_numero_partes_por_anyo(conn, anyo, mes) for mes in range(1, len(MESES) + 1)]

  fig, ax = plt.subplots(figsize=(9, 5))
  barras = ax.bar(MESES, partes, color="royalblue", edgecolor="blue", linewidth=0.5, width=0.6)
  
  ax.set_xlabel("Mes")
  ax.set_ylabel("Número de partes")
  ax.bar_label(barras, padding=3, fontsize=10)
      
  ax.grid(axis="y", linestyle="--", alpha=0.4)
  ax.set_axisbelow(True)
  ax.spines["top"].set_visible(False)
  ax.spines["right"].set_visible(False)
    
  fig.tight_layout()
    
  ruta_png = CARPETA_INFORMES_LEMS / str(anyo) / f"grafico_distribucion_partes_por_meses_y_anyo_{anyo}.png"
  ruta_png.parent.mkdir(parents=True, exist_ok=True)
  fig.savefig(ruta_png, dpi=150, bbox_inches="tight")   
  plt.close(fig)

  return ruta_png

def generar_grafico_distribucion_minutos_por_meses_y_anyo(conn: sqlite3.Connection, anyo: int) -> Path:       
  horas = [minutos_a_horas(contar_minutos_partes_por_anyo_mes(conn, anyo, mes)) for mes in range(1, len(MESES) + 1)]

  fig, ax = plt.subplots(figsize=(9, 5))
  barras = ax.bar(MESES, horas, color="orange", edgecolor="#e08a2c", linewidth=0.5, width=0.6)

  ax.set_xlabel("Mes")
  ax.set_ylabel("Horas")
  ax.bar_label(barras, padding=3, fontsize=10)
      
  ax.grid(axis="y", linestyle="--", alpha=0.4)
  ax.set_axisbelow(True)
  ax.spines["top"].set_visible(False)
  ax.spines["right"].set_visible(False)
    
  fig.tight_layout()
    
  ruta_png = CARPETA_INFORMES_LEMS / str(anyo) / f"grafico_distribucion_minutos_por_meses_y_anyo_{anyo}.png"
  ruta_png.parent.mkdir(parents=True, exist_ok=True)
  fig.savefig(ruta_png, dpi=150, bbox_inches="tight")   
  plt.close(fig)

  return ruta_png

def _imagen_escalada(ruta: Path) -> Image:
  """Imagen ajustada al ancho útil de la página, manteniendo la proporción."""
  ancho, alto = ImageReader(str(ruta)).getSize()
  return Image(str(ruta), width=ANCHO_UTIL, height=ANCHO_UTIL * alto / ancho)


def generar_grafico_distribucion_partes_por_anyo_dia_semana(conn: sqlite3.Connection, anyo: int) -> Path:
  partes = [contar_partes_por_anyo_dia_semana(conn, año=anyo, dia=dia) for dia in DIAS_SEMANA]

  fig, ax = plt.subplots(figsize=(9, 5))
  barras = ax.bar(DIAS_SEMANA, partes, color="mediumseagreen", edgecolor="darkgreen", linewidth=0.5, width=0.6)
  
  ax.set_xlabel("Día Semana")
  ax.set_ylabel("Número de partes")
  ax.bar_label(barras, padding=3, fontsize=10)  
      
  ax.grid(axis="y", linestyle="--", alpha=0.4)
  ax.set_axisbelow(True)
  ax.spines["top"].set_visible(False)
  ax.spines["right"].set_visible(False)
    
  fig.tight_layout()
    
  ruta_png = CARPETA_INFORMES_LEMS / str(anyo) / f"grafico_distribucion_partes_por_anyo_dia_semana_{anyo}.png"
  ruta_png.parent.mkdir(parents=True, exist_ok=True)
  fig.savefig(ruta_png, dpi=150, bbox_inches="tight")   
  plt.close(fig)
  return ruta_png

def generar_grafico_diagrama_sectores_distribucion_partes_por_anyo_dia_semana(conn: sqlite3.Connection, anyo: int) -> Path:
  partes = [contar_partes_por_anyo_dia_semana(conn, año=anyo, dia=dia) for dia in DIAS_SEMANA]

  dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
  colores = ["#1B5E20", "#2E7D32","#388E3C", "#43A047", "#66BB6A","#81C784", "#A5D6A7" ]

  fig, ax = plt.subplots(figsize=(9, 6))

  # Destaca ligeramente el día con más partes.
  mayor_actividad = partes.index(max(partes)) if any(partes) else -1
  explosion = [0.06 if i == mayor_actividad else 0 for i in range(len(partes))]

   # Dibuja el diagrama de sectores.
  sectores, textos, porcentajes = ax.pie(
    partes,
    labels=dias,
    colors=colores,
    autopct=lambda porcentaje: f"{porcentaje:.1f}%" if porcentaje > 0 else "",
    startangle=90,
    counterclock=False,
    explode=explosion,
    pctdistance=0.68,
    labeldistance=1.12,
    wedgeprops={"edgecolor": "white", "linewidth": 2},
    textprops={"fontsize": 10, "color": "#333333"}
  )

  # Resalta los porcentajes para facilitar su lectura.
  for texto in porcentajes:
    texto.set_fontsize(9)
    texto.set_fontweight("bold")
    texto.set_color("white")
    
  ax.axis("equal")
  fig.tight_layout()  
  ruta_png = CARPETA_INFORMES_LEMS / str(anyo) / f"grafico_diagrama_sectores_distribucion_partes_por_anyo_dia_semana_{anyo}.png"
  ruta_png.parent.mkdir(parents=True, exist_ok=True)
  fig.savefig(ruta_png, dpi=180, bbox_inches="tight", facecolor="white")
  plt.close(fig)
  return ruta_png




def generar_informe_actividad_de_lems_y_gtres(anyo: int) -> None:
  print(f"Generando informe de actividad de LEMS de {anyo}...")

  with sqlite3.connect(DB_PARTES) as conn:   
    grafico_distribucion_partes_por_meses_y_anyo = generar_grafico_distribucion_partes_por_meses_y_anyo(conn, anyo)
    grafico_distribucion_minutos_por_meses_y_anyo = generar_grafico_distribucion_minutos_por_meses_y_anyo(conn, anyo)   
    grafico_distribucion_partes_por_anyo_dia_semana = generar_grafico_distribucion_partes_por_anyo_dia_semana(conn, anyo)
    diagrama_sectores_partes_por_anyo_dia_semana = generar_grafico_diagrama_sectores_distribucion_partes_por_anyo_dia_semana(conn, anyo)
   
  contenido = [
    Paragraph(f"Informe de actividad de LEMS y GTRES {anyo}", estilo_titulo),
    Spacer(1, 0.8 * cm),

    Paragraph("Distribución mensual de los partes de trabajo", estilos["Heading2"]),        
    Paragraph(
      f"Análisis de la actividad mensual para identificar los periodos "
      f"con mayor y menor volumen de partes durante {anyo}.",
      estilos["BodyText"],      
    ),

    Spacer(1, 0.8 * cm),
    _imagen_escalada(grafico_distribucion_partes_por_meses_y_anyo),

    PageBreak(),
    Paragraph("Distribución mensual de las horas computadas en partes de trabajo", estilos["Heading2"]),
    Paragraph(
      f"El siguiente gráfico muestra el total de horas computadas "
      f"en los partes de trabajo durante cada mes de {anyo}.",
      estilos["BodyText"],
    ),    
    Spacer(1, 0.6 * cm),    
    _imagen_escalada(grafico_distribucion_minutos_por_meses_y_anyo),

    # Página 3 - Distribución de los partes por día de la semana
    PageBreak(),
    Paragraph("Distribución de los partes por día de la semana", estilos["Heading2"]),
    Paragraph(
      f"Análisis de la distribución de los partes de trabajo por día de la semana "
      "que permite identificar los días con mayor y menor actividad.",
      estilos["BodyText"],
    ),
    Spacer(1, 0.6 * cm),
    _imagen_escalada(grafico_distribucion_partes_por_anyo_dia_semana),
    _imagen_escalada(diagrama_sectores_partes_por_anyo_dia_semana),


  ]    
 
  carpeta = CARPETA_INFORMES_LEMS / str(anyo) / f"informe de actividad de lems y gtres {anyo}.pdf"
  
  SimpleDocTemplate(
    str(carpeta),
    pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title=f"Informe de actividad de LEMS y GTRES {anyo}",
  ).build(contenido, onFirstPage=pie_pagina, onLaterPages=pie_pagina)  
