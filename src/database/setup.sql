CREATE TABLE partes_temp (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  numero INTEGER NOT NULL,
  fecha DATE,
  cliente CHAR(255) NOT NULL,
  tecnico CHAR(50) NOT NULL,
  minutos INTEGER NOT NULL,
  desplazamiento CHAR(2) NOT NULL,
  minutos_desplazamiento INTEGER NOT NULL,
  duracion_total INTEGER NOT NULL,
  tecnicos INTEGER NOT NULL,
  mes INTEGER NOT NULL,
  año INTEGER NOT NULL,
  trimestre INTEGER NOT NULL,
  dia_semana CHAR(1) NOT NULL
);

CREATE INDEX idx_partes_temp_cliente ON partes_temp(cliente);
CREATE INDEX idx_partes_temp_desplazamiento ON partes_temp(desplazamiento);

CREATE TABLE partes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  numero INTEGER NOT NULL,
  fecha DATE,
  cliente CHAR(255) NOT NULL,
  tecnico CHAR(50) NOT NULL,
  minutos INTEGER NOT NULL,
  desplazamiento INTEGER NOT NULL,
  duracion_total INTEGER NOT NULL,  
  mes INTEGER NOT NULL,
  año INTEGER NOT NULL,
  trimestre INTEGER NOT NULL,
  dia_semana CHAR(1) NOT NULL
);

CREATE INDEX idx_partes_mes ON partes(mes);
CREATE INDEX idx_partes_anyo ON partes(año);
CREATE INDEX idx_partes_dia_semana ON partes(dia_semana);
