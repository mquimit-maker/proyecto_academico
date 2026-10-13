"""CONTROLADOR: reglas del negocio y las 5 operaciones. NUNCA usa print() ni input().
Toda operación devuelve la TUPLA (exito, mensaje) o datos."""
import os

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido

# ---------------------------------------------------------------------
# Gestores: la única puerta hacia los archivos JSON
# ---------------------------------------------------------------------
CARPETA_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
gestor_estudiantes = GestorJSON(os.path.join(CARPETA_DATOS, "estudiantes.json"))
gestor_materias = GestorJSON(os.path.join(CARPETA_DATOS, "materias.json"))
gestor_matriculas = GestorJSON(os.path.join(CARPETA_DATOS, "matriculas.json"))

# TUPLAS: son listas fijas de nombres de campo; nadie debe modificarlas en
# ejecución, por eso son tupla y no lista.
CAMPOS_BUSCABLES_ESTUDIANTE = ("nombre", "apellido", "email", "carnet", "carrera")
CAMPOS_BUSCABLES_MATERIA = ("nombre", "codigo")
OBLIGATORIOS_ESTUDIANTE = ("nombre", "apellido", "email", "carnet")
OBLIGATORIOS_MATERIA = ("nombre", "codigo", "creditos")
CAMPOS_ESTUDIANTE = ("nombre", "apellido", "email", "carnet", "carrera")
CAMPOS_MATERIA = ("nombre", "codigo", "creditos", "cupos")


# =====================================================================
# FUNCIONES GENÉRICAS (funcionan con CUALQUIER modelo gracias a la herencia)
# =====================================================================
def leer_objetos(gestor, clase):
    """Lista de diccionarios del JSON -> lista de objetos de `clase`.
    Usa desde_diccionario(), el método de clase heredado de ModeloBase."""
    objetos = []
    for registro in gestor.leer():
        objetos.append(clase.desde_diccionario(registro))
    return objetos


def obtener_por_id(gestor, clase, id_registro):
    for registro in gestor.leer():
        if registro["id"] == id_registro:
            return clase.desde_diccionario(registro)
    return None


def buscar(gestor, clase, termino, campos):
    """Búsqueda lineal: devuelve los objetos que contengan `termino` en algún campo."""
    termino = termino.strip().lower()
    encontrados = []
    if termino == "":
        return encontrados
    for objeto in leer_objetos(gestor, clase):
        for campo in campos:
            if termino in str(getattr(objeto, campo)).lower():
                encontrados.append(objeto)
                break                      # ya coincidió, no repetirlo
    return encontrados


def siguiente_id(gestor):
    mayor = 0
    for registro in gestor.leer():
        if registro["id"] > mayor:
            mayor = registro["id"]
    return mayor + 1


def guardar_nuevo(gestor, objeto):
    datos = gestor.leer()
    datos.append(objeto.a_diccionario())
    return gestor.guardar(datos)


def reemplazar(gestor, objeto):
    """Cambia el registro que tiene el mismo id. Hay que llamarla tras modificar un objeto."""
    datos = gestor.leer()
    for posicion, registro in enumerate(datos):
        if registro["id"] == objeto.id:
            datos[posicion] = objeto.a_diccionario()
            return gestor.guardar(datos)
    return False


def eliminar(gestor, id_registro):
    datos = gestor.leer()
    # Lista NUEVA sin el registro: nunca se borra mientras se recorre
    restantes = [r for r in datos if r["id"] != id_registro]
    if len(restantes) == len(datos):
        return False
    return gestor.guardar(restantes)


def ids_registrados(gestor):
    """CONJUNTO de ids: preguntar 'x in conjunto' es instantáneo y no hay repetidos."""
    return {registro["id"] for registro in gestor.leer()}


def indice_por_id(gestor, clase):
    """DICCIONARIO {id: objeto}: acceso directo por id, sin recorrer la lista."""
    return {objeto.id: objeto for objeto in leer_objetos(gestor, clase)}


def es_entero(valor):
    return str(valor).strip().isdigit()


# =====================================================================
# ESTUDIANTES
# =====================================================================
def carnets_registrados(excepto_id=None):
    """CONJUNTO de carnets ya usados: preguntar 'x in conjunto' es instantáneo
    y el conjunto descarta repetidos solo."""
    return {r.get("carnet", "").upper() for r in gestor_estudiantes.leer()
            if r["id"] != excepto_id}


def emails_registrados(excepto_id=None):
    """CONJUNTO de emails de los OTROS estudiantes (para no chocar con uno mismo al editar)."""
    return {r.get("email", "").lower() for r in gestor_estudiantes.leer()
            if r["id"] != excepto_id}


def validar_estudiante(datos, id_actual=None):
    """Devuelve un MENSAJE de error, o None si todo está bien."""
    # 1) obligatorios: al crear, todos; al actualizar, los que vengan en `datos`
    for campo in OBLIGATORIOS_ESTUDIANTE:
        if id_actual is None or campo in datos:
            if str(datos.get(campo, "")).strip() == "":
                return f"El campo {campo} es obligatorio"
    # 2) email válido y único
    if "email" in datos:
        email = str(datos["email"]).strip().lower()
        if not es_email_valido(email):
            return f"Email inválido: '{email}'"
        if email in emails_registrados(id_actual):
            return "Ese email ya está registrado"
    # 3) carnet único
    if "carnet" in datos:
        carnet = str(datos["carnet"]).strip().upper()
        if carnet in carnets_registrados(id_actual):
            return "Ese carnet ya está registrado"
    return None


def crear_estudiante(datos):
    error = validar_estudiante(datos)
    if error:
        return False, error
    estudiante = Estudiante(siguiente_id(gestor_estudiantes),
                            str(datos["nombre"]).strip().title(),
                            str(datos["apellido"]).strip().title(),
                            str(datos["email"]).strip().lower(),
                            str(datos["carnet"]).strip().upper(),
                            str(datos.get("carrera", "")).strip().title())
    if not guardar_nuevo(gestor_estudiantes, estudiante):
        return False, "No se pudo guardar el archivo"
    return True, f"Estudiante creado: {estudiante.etiqueta()}"


def obtener_estudiantes():
    return leer_objetos(gestor_estudiantes, Estudiante)


def obtener_estudiante(id_estudiante):
    return obtener_por_id(gestor_estudiantes, Estudiante, id_estudiante)


def buscar_estudiantes(termino):
    return buscar(gestor_estudiantes, Estudiante, termino, CAMPOS_BUSCABLES_ESTUDIANTE)


def actualizar_estudiante(id_estudiante, cambios):
    estudiante = obtener_estudiante(id_estudiante)
    if estudiante is None:
        return False, f"No existe un estudiante con id {id_estudiante}"
    if not cambios:
        return False, "No se indicó ningún cambio"
    # DIFERENCIA de conjuntos: campos que no existen en un estudiante
    desconocidos = set(cambios) - set(CAMPOS_ESTUDIANTE)
    if desconocidos:
        return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"
    # Se valida ANTES de tocar el objeto: si algo falla, no cambia nada
    error = validar_estudiante(cambios, id_estudiante)
    if error:
        return False, error
    for campo, valor in cambios.items():
        valor = str(valor).strip()
        if campo in ("nombre", "apellido", "carrera"):
            valor = valor.title()
        elif campo == "email":
            valor = valor.lower()
        elif campo == "carnet":
            valor = valor.upper()
        setattr(estudiante, campo, valor)
    reemplazar(gestor_estudiantes, estudiante)
    return True, f"Estudiante {id_estudiante} actualizado"


def eliminar_estudiante(id_estudiante):
    if obtener_estudiante(id_estudiante) is None:
        return False, f"No existe un estudiante con id {id_estudiante}"
    eliminar(gestor_estudiantes, id_estudiante)
    return True, f"Estudiante {id_estudiante} eliminado"


def carreras():
    """CONJUNTO de carreras: sin repetidos. sorted() lo devuelve como lista ordenada."""
    return sorted({e.carrera for e in obtener_estudiantes() if e.carrera != ""})


# =====================================================================
# MATERIAS
# =====================================================================
def codigos_registrados(excepto_id=None):
    """CONJUNTO de códigos ya usados: pertenencia instantánea y sin repetidos."""
    return {r.get("codigo", "").upper() for r in gestor_materias.leer()
            if r["id"] != excepto_id}


def validar_materia(datos, id_actual=None):
    for campo in OBLIGATORIOS_MATERIA:
        if id_actual is None or campo in datos:
            if str(datos.get(campo, "")).strip() == "":
                return f"El campo {campo} es obligatorio"
    if "nombre" in datos and str(datos["nombre"]).strip() == "":
        return "El campo nombre es obligatorio"
    if "codigo" in datos:
        codigo = str(datos["codigo"]).strip().upper()
        if codigo in codigos_registrados(id_actual):
            return f"Ya existe una materia con el código {codigo}"
    if "creditos" in datos:
        if not es_entero(datos["creditos"]) or not 1 <= int(datos["creditos"]) <= 10:
            return "Los créditos deben ser un entero entre 1 y 10"
    if str(datos.get("cupos", "")).strip() != "":
        if (not es_entero(datos["cupos"])
                or int(datos["cupos"]) > Materia.CUPOS_MAXIMOS):
            return f"Los cupos deben ser un entero entre 0 y {Materia.CUPOS_MAXIMOS}"
    return None


def crear_materia(datos):
    error = validar_materia(datos)
    if error:
        return False, error
    # Si no escriben los cupos, la materia empieza con el máximo permitido
    cupos = str(datos.get("cupos", "")).strip()
    materia = Materia(siguiente_id(gestor_materias),
                      str(datos["nombre"]).strip().title(),
                      str(datos["codigo"]).strip().upper(),
                      int(datos["creditos"]),
                      int(cupos) if cupos != "" else Materia.CUPOS_MAXIMOS)
    if not guardar_nuevo(gestor_materias, materia):
        return False, "No se pudo guardar el archivo"
    return True, f"Materia creada: {materia.etiqueta()}"


def obtener_materias():
    return leer_objetos(gestor_materias, Materia)


def obtener_materia(id_materia):
    return obtener_por_id(gestor_materias, Materia, id_materia)


def buscar_materias(termino):
    return buscar(gestor_materias, Materia, termino, CAMPOS_BUSCABLES_MATERIA)


def actualizar_materia(id_materia, cambios):
    materia = obtener_materia(id_materia)
    if materia is None:
        return False, f"No existe una materia con id {id_materia}"
    if not cambios:
        return False, "No se indicó ningún cambio"
    desconocidos = set(cambios) - set(CAMPOS_MATERIA)
    if desconocidos:
        return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"
    error = validar_materia(cambios, id_materia)
    if error:
        return False, error
    if "nombre" in cambios:
        materia.nombre = str(cambios["nombre"]).strip().title()
    if "codigo" in cambios:
        materia.codigo = str(cambios["codigo"]).strip().upper()
    if "creditos" in cambios:
        materia.creditos = int(cambios["creditos"])
    if "cupos" in cambios:
        materia.cupos = int(cambios["cupos"])
    reemplazar(gestor_materias, materia)
    return True, f"Materia {id_materia} actualizada"


def eliminar_materia(id_materia):
    if obtener_materia(id_materia) is None:
        return False, f"No existe una materia con id {id_materia}"
    eliminar(gestor_materias, id_materia)
    return True, f"Materia {id_materia} eliminada"


def materias_sin_cupo():
    sin_cupo = []
    for materia in obtener_materias():
        if not materia.hay_cupo():
            sin_cupo.append(materia)
    return sin_cupo


# =====================================================================
# MATRÍCULAS
# =====================================================================
def matriculas_registradas():
    """CONJUNTO de tuplas (estudiante_id, materia_id, periodo).
    Sirve para detectar un duplicado comparando los TRES datos juntos."""
    return {(r["estudiante_id"], r["materia_id"], r["periodo"])
            for r in gestor_matriculas.leer()}


def validar_matricula(datos):
    try:
        estudiante_id = int(datos.get("estudiante_id", 0))
        materia_id = int(datos.get("materia_id", 0))
    except (TypeError, ValueError):
        return "estudiante_id y materia_id deben ser números enteros"
    periodo = str(datos.get("periodo", "")).strip()
    if periodo == "":
        return "El periodo es obligatorio (ej. 2026-1)"
    if estudiante_id not in ids_registrados(gestor_estudiantes):      # conjunto
        return f"No existe un estudiante con id {estudiante_id}"
    materia = obtener_materia(materia_id)
    if materia is None:
        return f"No existe una materia con id {materia_id}"
    if (estudiante_id, materia_id, periodo) in matriculas_registradas():
        return "Ese estudiante ya está matriculado en esa materia en ese periodo"
    if not materia.hay_cupo():
        return f"No quedan cupos en {materia.nombre}"
    return None


def crear_matricula(datos):
    error = validar_matricula(datos)
    if error:
        return False, error
    materia = obtener_materia(int(datos["materia_id"]))
    matricula = Matricula(siguiente_id(gestor_matriculas),
                          int(datos["estudiante_id"]),
                          materia.id,
                          str(datos["periodo"]).strip())
    materia.ocupar_cupo()
    reemplazar(gestor_materias, materia)          # guarda el cupo nuevo en materias.json
    guardar_nuevo(gestor_matriculas, matricula)   # guarda la matrícula en matriculas.json
    return True, f"Matrícula {matricula.id} registrada. Cupos restantes: {materia.cupos}"


def obtener_matriculas():
    return leer_objetos(gestor_matriculas, Matricula)


def obtener_matricula(id_matricula):
    return obtener_por_id(gestor_matriculas, Matricula, id_matricula)


def registrar_nota(id_matricula, nota):
    matricula = obtener_matricula(id_matricula)
    if matricula is None:
        return False, f"No existe la matrícula {id_matricula}"
    nota = str(nota).strip().replace(",", ".")        # acepta 16,5 y 16.5
    if not Materia.es_nota_valida(nota):              # método ESTÁTICO de Materia
        return False, "La nota debe ser un número entre 0 y 20"
    matricula.nota = round(float(nota), 2)
    reemplazar(gestor_matriculas, matricula)
    return True, f"Nota {matricula.nota:.1f} registrada: {matricula.estado()}"


def retirar_matricula(id_matricula):
    """Borra la matrícula y devuelve el cupo a la materia."""
    matricula = obtener_matricula(id_matricula)
    if matricula is None:
        return False, f"No existe la matrícula {id_matricula}"
    materia = obtener_materia(matricula.materia_id)
    if materia is not None:
        materia.liberar_cupo()
        reemplazar(gestor_materias, materia)
    eliminar(gestor_matriculas, id_matricula)
    return True, f"Matrícula {id_matricula} retirada y cupo liberado"


def certificado(id_matricula):
    matricula = obtener_matricula(id_matricula)
    if matricula is None:
        return None
    # DICCIONARIOS ÍNDICE {id: objeto}: acceso directo, sin recorrer listas
    estudiantes = indice_por_id(gestor_estudiantes, Estudiante)
    materias = indice_por_id(gestor_materias, Materia)
    estudiante = estudiantes.get(matricula.estudiante_id)
    materia = materias.get(matricula.materia_id)
    nota = "-" if matricula.nota is None else f"{matricula.nota:.1f}"
    texto = f"CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n"
    if estudiante:
        texto += f"Estudiante: {estudiante.nombre_completo()}   ({estudiante.carnet})\n"
    else:
        texto += "Estudiante: (eliminado)\n"
    if materia:
        texto += f"Materia   : {materia.nombre}   ({materia.codigo}) · {materia.creditos} créditos\n"
    else:
        texto += "Materia   : (eliminada)\n"
    texto += "-" * 42 + "\n"
    texto += f"Nota      : {nota}\n"
    texto += f"Estado    : {matricula.estado()}"
    return texto


def matriculas_por_estudiante():
    """DICCIONARIO DE LISTAS {estudiante_id: [matrículas]}: una clave por estudiante,
    con todas sus matrículas juntas. setdefault crea la lista la primera vez."""
    agrupadas = {}
    for matricula in obtener_matriculas():
        agrupadas.setdefault(matricula.estudiante_id, []).append(matricula)
    return agrupadas


def promedio_de_estudiante(id_estudiante):
    """Promedio de las notas ya registradas, o None si todavía no tiene ninguna."""
    matriculas = matriculas_por_estudiante().get(id_estudiante, [])
    notas = [m.nota for m in matriculas if m.nota is not None]
    if not notas:
        return None
    return round(sum(notas) / len(notas), 2)


def total_aprobadas():
    total = 0
    for matricula in obtener_matriculas():
        if matricula.esta_aprobada():
            total += 1
    return total
