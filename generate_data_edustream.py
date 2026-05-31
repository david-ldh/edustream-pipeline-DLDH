"""
generate_data.py
================
Genera datos de prueba para una plataforma de cursos online y los guarda
como archivos CSV en la carpeta `data/`.

Archivos generados
------------------
enrollments.csv  — inscripciones de usuarios a cursos
    Campos: enrollment_id, user_id, course_id, enrolled_at, payment_amount, currency
    Calidad simulada:
      · ~3 % de filas con enrollment_id nulo  (registros sin identificador)
      · ~3 % de filas con user_id nulo        (usuario no identificado)
      · ~3 % de filas con course_id nulo      (curso no identificado)
      · payment_amount nulo en cursos gratuitos y ~8 % adicional de pagos omitidos
      · Los nulos en los tres IDs son independientes entre sí

courses.csv      — catálogo de cursos
    Campos: course_id, title, instructor_id, category, price_usd, language
    Calidad simulada:
      · ~9 % de cursos con category en blanco
      · ~10 % de cursos gratuitos (price_usd = 0)

progress.csv     — progreso de cada usuario por curso
    Campos: user_id, course_id, lessons_completed, total_lessons, last_activity_at
    Calidad simulada:
      · total_lessons = 0 representa dato corrupto (según especificación)

instructors.csv  — datos de instructores
    Campos: instructor_id, name, country, joined_at
    Calidad simulada:
      · ~15 % de instructores con country = NULL

Uso
---
    python generate_data.py

Requisitos: Python 3.7+ (solo librería estándar).
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Directorio de salida; se crea si no existe
OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

# Semilla para reproducibilidad
SEED = 29
random.seed(SEED)

# -- Tamaños de dataset --------------------------------------------------------
N_INSTRUCTORS = 200
N_COURSES     = 300
N_USERS       = 1000
N_ENROLLMENTS = 5000

# -- Rango temporal de los datos -----------------------------------------------
START = datetime(2020, 1, 1)
END   = datetime(2025, 12, 31)

# -- Catálogos de valores posibles --------------------------------------------

# None aparece dos veces para aumentar la probabilidad de country nulo (~15 %)
COUNTRIES = [
    "Mexico", "Colombia", "Argentina", "España", "Peru", "Chile",
    "Brasil", "USA", "Venezuela", "Ecuador", "Bolivia", None, None,
]

# Cadena vacía representa category en blanco (~9 %)
CATEGORIES = [
    "Programacion", "Data Science", "Diseño", "Marketing", "Negocios",
    "Idiomas", "Musica", "Fotografia", "DevOps", "Ciberseguridad", "",
]

LANGUAGES  = ["Español", "Ingles", "Portugues", "Frances"]
CURRENCIES = ["USD", "MXN", "COP", "ARS", "BRL", "PEN"]

FIRST_NAMES = [
    "Ana", "Luis", "Maria", "Carlos", "Sofia", "Juan", "Valeria",
    "Pedro", "Camila", "Jorge", "Fernanda", "Diego", "Laura", "Andres",
    "Gabriela", "Roberto", "Daniela", "Miguel", "Paola", "Ricardo",
]

LAST_NAMES = [
    "Garcia", "Rodriguez", "Martinez", "Lopez", "Hernandez", "Gonzalez",
    "Perez", "Sanchez", "Ramirez", "Torres", "Flores", "Rivera",
    "Gomez", "Diaz", "Cruz", "Morales", "Reyes", "Gutierrez", "Vargas",
]

COURSE_PREFIXES = [
    "Introduccion a", "Curso avanzado de", "Fundamentos de",
    "Masterclass de", "Bootcamp de", "Taller practico de",
    "Guia completa de", "De cero a experto en",
]

# Topics agrupados por categoría para garantizar coherencia temática
TOPICS_BY_CATEGORY = {
    "Programacion":   ["Python", "JavaScript", "React", "FastAPI", "TypeScript", "Java", "C#", "Git"],
    "Data Science":   ["Python", "SQL", "Machine Learning", "Tableau", "Power BI", "Deep Learning", "NLP", "Estadistica"],
    "Diseño":         ["Figma", "Photoshop", "Illustrator", "UX/UI", "Canva", "After Effects"],
    "Marketing":      ["Google Analytics", "SEO", "Copywriting", "Email Marketing", "Google Ads", "Social Media"],
    "Negocios":       ["Excel", "Liderazgo", "Finanzas personales", "Emprendimiento", "Gestion de proyectos", "Power BI"],
    "Idiomas":        ["Ingles", "Frances", "Aleman", "Italiano", "Mandarin", "Portugues"],
    "Musica":         ["Guitarra", "Piano", "Produccion Musical", "Canto", "Bateria", "Composicion Musical"],
    "Fotografia":     ["Fotografia de retrato", "Fotografia urbana", "Lightroom", "Edicion de fotos", "Photoshop"],
    "DevOps":         ["Docker", "Kubernetes", "AWS", "Git", "CI/CD", "Terraform", "Linux"],
    "Ciberseguridad": ["Ethical Hacking", "Seguridad en redes", "Criptografia", "OWASP", "Pentesting", "Forense digital"],
    "":               ["Excel", "Git", "Python", "Figma", "SQL", "Photoshop", "Google Analytics"],
}


# -- Helpers -------------------------------------------------------------------

def random_date(start: datetime, end: datetime) -> datetime:
    """Devuelve un datetime aleatorio uniforme en [start, end]."""
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def fmt(dt: datetime) -> str:
    """Formatea un datetime como string ISO sin zona horaria."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def random_name() -> str:
    """Combina un nombre y apellido aleatorio del catálogo."""
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


# -- Generadores ---------------------------------------------------------------

def generate_instructors() -> list[str]:
    """
    Crea instructors.csv con N_INSTRUCTORS filas.
    Devuelve la lista de instructor_id generados para usarla en courses.
    """
    rows = []
    for i in range(1, N_INSTRUCTORS + 1):
        rows.append({
            "instructor_id": f"INS{i:04d}",
            "name":          random_name(),
            "country":       random.choice(COUNTRIES),  # puede ser None → celda vacía
            "joined_at":     fmt(random_date(START, END)),
        })

    path = OUTPUT_DIR / "instructors.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["instructor_id", "name", "country", "joined_at"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] {path}  ({len(rows)} filas)")
    return [r["instructor_id"] for r in rows]


def generate_courses(instructor_ids: list[str]) -> list[dict]:
    """
    Crea courses.csv con N_COURSES filas.
    El 10 % de los cursos son gratuitos (price_usd = 0).
    Devuelve las filas como lista de dicts para usarlas en enrollments.
    """
    rows = []
    for i in range(1, N_COURSES + 1):
        # 10 % de probabilidad de curso gratuito
        price    = round(random.uniform(9.99, 199.99), 2) if random.random() > 0.1 else 0.0
        category = random.choice(CATEGORIES)
        topic    = random.choice(TOPICS_BY_CATEGORY[category])
        rows.append({
            "course_id":     f"CRS{i:04d}",
            "title":         f"{random.choice(COURSE_PREFIXES)} {topic}",
            "instructor_id": random.choice(instructor_ids),
            "category":      category,
            "price_usd":     price,
            "language":      random.choice(LANGUAGES),
        })

    path = OUTPUT_DIR / "courses.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["course_id", "title", "instructor_id", "category", "price_usd", "language"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] {path}  ({len(rows)} filas)")
    return rows


def generate_enrollments(course_rows: list[dict]) -> list[dict]:
    """
    Crea enrollments.csv con N_ENROLLMENTS filas únicas (user_id, course_id).
    - Cursos gratuitos → payment_amount y currency vacíos.
    - ~8 % de cursos de pago también tienen payment_amount vacío (datos faltantes).
    - ~3 % de filas tienen enrollment_id, user_id o course_id nulo (datos corruptos).
    Devuelve las filas para generar progress.csv.
    """
    user_ids     = [f"USR{i:05d}" for i in range(1, N_USERS + 1)]
    course_ids   = [r["course_id"] for r in course_rows]
    free_courses = {r["course_id"] for r in course_rows if r["price_usd"] == 0.0}

    seen = set()   # evita duplicados (user_id, course_id)
    rows = []
    attempts = 0

    while len(rows) < N_ENROLLMENTS and attempts < N_ENROLLMENTS * 10:
        attempts += 1
        uid = random.choice(user_ids)
        cid = random.choice(course_ids)

        if (uid, cid) in seen:
            continue
        seen.add((uid, cid))

        if cid in free_courses or random.random() < 0.08:
            payment  = None
            currency = None
        else:
            payment  = round(random.uniform(5.0, 199.99), 2)
            currency = random.choice(CURRENCIES)

        # ~3 % de probabilidad de nulo en cada campo identificador
        enrollment_id = "" if random.random() < 0.03 else f"ENR{len(rows)+1:06d}"
        row_uid       = "" if random.random() < 0.03 else uid
        row_cid       = "" if random.random() < 0.03 else cid

        rows.append({
            "enrollment_id":  enrollment_id,
            "user_id":        row_uid,
            "course_id":      row_cid,
            "enrolled_at":    fmt(random_date(START, END)),
            "payment_amount": payment  if payment  is not None else "",
            "currency":       currency if currency is not None else "",
        })

    path = OUTPUT_DIR / "enrollments.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["enrollment_id", "user_id", "course_id", "enrolled_at", "payment_amount", "currency"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] {path}  ({len(rows)} filas)")
    return rows


def generate_progress(enrollment_rows: list[dict]) -> None:
    """
    Crea progress.csv con una fila por inscripción.
    total_lessons = 0 simula datos corruptos (según especificación).
    """
    rows = []
    for enr in enrollment_rows:
        total     = random.randint(0, 60)
        # si total es 0 (dato corrupto), completed también es 0
        completed = 0 if total == 0 else random.randint(0, total)
        rows.append({
            "user_id":           enr["user_id"],
            "course_id":         enr["course_id"],
            "lessons_completed": completed,
            "total_lessons":     total,
            "last_activity_at":  fmt(random_date(START, END)),
        })

    path = OUTPUT_DIR / "progress.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["user_id", "course_id", "lessons_completed", "total_lessons", "last_activity_at"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] {path}  ({len(rows)} filas)")


# -- Entry point ---------------------------------------------------------------

if __name__ == "__main__":
    print("Generando datos de prueba...\n")
    instructor_ids  = generate_instructors()
    course_rows     = generate_courses(instructor_ids)
    enrollment_rows = generate_enrollments(course_rows)
    generate_progress(enrollment_rows)

    # Tabla resumen con conteo real leído desde cada archivo generado
    print("\n" + "-" * 42)
    print(f"{'Archivo':<22} {'Registros':>10}")
    print("-" * 42)
    for csv_file in ["instructors.csv", "courses.csv", "enrollments.csv", "progress.csv"]:
        path = OUTPUT_DIR / csv_file
        with open(path, encoding="utf-8") as f:
            count = sum(1 for _ in f) - 1  # descuenta el header
        print(f"{csv_file:<22} {count:>10,}")
    print("-" * 42)
    print(f"\nArchivos en: {OUTPUT_DIR.resolve()}")
