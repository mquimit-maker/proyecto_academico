"""VISTA: menús, input() y print(). No valida reglas ni abre archivos."""
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
import views


# =====================================================================
# AYUDAS DE PANTALLA
# =====================================================================
def pausa():
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta):
    """Devuelve un entero o None si el usuario escribió otra cosa."""
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito, mensaje):
    # Los controladores devuelven la TUPLA (exito, mensaje)
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavía."):
    """Sirve para estudiantes, materias y matrículas: cada modelo sabe mostrarse."""
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        print(f"  {objeto}")
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<16}: {valor}")


# =====================================================================
# MENÚ DE ESTUDIANTES
# =====================================================================
def crear_estudiante():
    imprimir_titulo("CREAR ESTUDIANTE")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "carnet": input("Carnet (ej. EST2026001): "),
        "carrera": input("Carrera: "),
    }
    mostrar_resultado(*views.crear_estudiante(datos))
    pausa()


def listar_estudiantes():
    imprimir_titulo("ESTUDIANTES")
    mostrar_lista(views.obtener_estudiantes(), "Todavía no hay estudiantes.")
    pausa()


def buscar_estudiante():
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, apellido, email, carnet o carrera: ")
    mostrar_lista(views.buscar_estudiantes(termino),
                  f"Ningún estudiante coincide con '{termino}'.")
    pausa()


def ver_estudiante():
    imprimir_titulo("VER ESTUDIANTE POR ID")
    id_estudiante = pedir_entero("Id: ")
    estudiante = views.obtener_estudiante(id_estudiante)
    if estudiante is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(estudiante)
        promedio = views.promedio_de_estudiante(estudiante.id)
        imprimir_info(f"Promedio: {promedio if promedio is not None else 'sin notas todavía'}")
    pausa()


def actualizar_estudiante():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    id_estudiante = pedir_entero("Id: ")
    estudiante = views.obtener_estudiante(id_estudiante)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()
    imprimir_info(f"Editando: {estudiante.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")
    cambios = {}
    for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
        actual = getattr(estudiante, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo
    mostrar_resultado(*views.actualizar_estudiante(id_estudiante, cambios))
    pausa()


def eliminar_estudiante():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    id_estudiante = pedir_entero("Id: ")
    estudiante = views.obtener_estudiante(id_estudiante)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()
    imprimir_info(f"Se eliminará: {estudiante.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*views.eliminar_estudiante(id_estudiante))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# =====================================================================
# MENÚ DE MATERIAS
# =====================================================================
def crear_materia():
    imprimir_titulo("CREAR MATERIA")
    datos = {
        "nombre": input("Nombre: "),
        "codigo": input("Código (ej. MAT101): "),
        "creditos": input("Créditos (1-10): "),
        "cupos": input("Cupos (vacío = 30): "),
    }
    mostrar_resultado(*views.crear_materia(datos))
    pausa()


def listar_materias():
    imprimir_titulo("MATERIAS")
    mostrar_lista(views.obtener_materias(), "Todavía no hay materias.")
    pausa()


def buscar_materia():
    imprimir_titulo("BUSCAR MATERIA")
    termino = input("Nombre o código: ")
    mostrar_lista(views.buscar_materias(termino), "Sin coincidencias.")
    pausa()


def ver_materia():
    imprimir_titulo("VER MATERIA POR ID")
    materia = views.obtener_materia(pedir_entero("Id: "))
    if materia is None:
        imprimir_error("No encontrada")
    else:
        mostrar_detalle(materia)
    pausa()


def actualizar_materia():
    imprimir_titulo("ACTUALIZAR MATERIA")
    id_materia = pedir_entero("Id: ")
    materia = views.obtener_materia(id_materia)
    if materia is None:
        imprimir_error("No encontrada")
        return pausa()
    imprimir_info(f"Editando: {materia.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")
    cambios = {}
    for campo in ("nombre", "codigo", "creditos", "cupos"):
        actual = getattr(materia, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo
    mostrar_resultado(*views.actualizar_materia(id_materia, cambios))
    pausa()


def eliminar_materia():
    imprimir_titulo("ELIMINAR MATERIA")
    id_materia = pedir_entero("Id: ")
    materia = views.obtener_materia(id_materia)
    if materia is None:
        imprimir_error("No encontrada")
        return pausa()
    imprimir_info(f"Se eliminará: {materia.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*views.eliminar_materia(id_materia))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# =====================================================================
# MENÚ DE MATRÍCULAS
# =====================================================================
def matricular():
    imprimir_titulo("MATRICULAR")
    imprimir_info("Estudiantes:")
    mostrar_lista(views.obtener_estudiantes())
    imprimir_info("Materias:")
    mostrar_lista(views.obtener_materias())
    datos = {
        "estudiante_id": pedir_entero("\nId del estudiante: "),
        "materia_id": pedir_entero("Id de la materia: "),
    }
    if None in datos.values():
        imprimir_error("Los ids deben ser números enteros")
        return pausa()
    datos["periodo"] = input("Periodo (ej. 2026-1): ")
    mostrar_resultado(*views.crear_matricula(datos))
    pausa()


def listar_matriculas():
    imprimir_titulo("MATRÍCULAS")
    mostrar_lista(views.obtener_matriculas(), "Todavía no hay matrículas.")
    pausa()


def registrar_nota():
    imprimir_titulo("REGISTRAR NOTA")
    mostrar_lista(views.obtener_matriculas(), "Todavía no hay matrículas.")
    id_matricula = pedir_entero("\nId de la matrícula: ")
    if id_matricula is None:
        imprimir_error("El id debe ser un número entero")
        return pausa()
    nota = input("Nota (0 a 20): ")
    mostrar_resultado(*views.registrar_nota(id_matricula, nota))
    pausa()


def ver_certificado():
    imprimir_titulo("CERTIFICADO")
    texto = views.certificado(pedir_entero("Id de la matrícula: "))
    if texto is None:
        imprimir_error("No existe esa matrícula")
    else:
        print(texto)
    pausa()


def retirar_matricula():
    imprimir_titulo("RETIRAR MATRÍCULA")
    id_matricula = pedir_entero("Id de la matrícula: ")
    if id_matricula and confirmar("Se liberará el cupo. ¿Confirma?"):
        mostrar_resultado(*views.retirar_matricula(id_matricula))
    else:
        imprimir_info("Operación cancelada")
    pausa()


def resumen():
    imprimir_titulo("RESUMEN")
    print(f"  Estudiantes      : {len(views.obtener_estudiantes())}")
    print(f"  Carreras         : {', '.join(views.carreras()) or '-'}")
    print(f"  Materias         : {len(views.obtener_materias())}")
    sin_cupo = views.materias_sin_cupo()
    print(f"  Materias sin cupo: {', '.join(m.nombre for m in sin_cupo) or 'ninguna'}")
    print(f"  Matrículas       : {len(views.obtener_matriculas())}")
    print(f"  Aprobadas        : {views.total_aprobadas()}")
    pausa()


# =====================================================================
# MENÚS: DICCIONARIOS tecla -> (texto, función)
# =====================================================================
MENU_ESTUDIANTES = {
    "1": ("Crear estudiante", crear_estudiante),
    "2": ("Ver todos", listar_estudiantes),
    "3": ("Buscar", buscar_estudiante),
    "4": ("Ver por id", ver_estudiante),
    "5": ("Actualizar", actualizar_estudiante),
    "6": ("Eliminar", eliminar_estudiante),
    "0": ("Volver", None),
}
MENU_MATERIAS = {
    "1": ("Crear materia", crear_materia),
    "2": ("Ver todas", listar_materias),
    "3": ("Buscar", buscar_materia),
    "4": ("Ver por id", ver_materia),
    "5": ("Actualizar", actualizar_materia),
    "6": ("Eliminar", eliminar_materia),
    "0": ("Volver", None),
}
MENU_MATRICULAS = {
    "1": ("Matricular", matricular),
    "2": ("Ver todas", listar_matriculas),
    "3": ("Registrar nota", registrar_nota),
    "4": ("Ver certificado", ver_certificado),
    "5": ("Retirar matrícula", retirar_matricula),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo, opciones):
    """Un solo bucle para los tres submenús."""
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _funcion) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()
        tecla = input("Opción: ").strip()
        if tecla not in opciones:
            imprimir_error("Opción no válida")
            pausa()
            continue
        _texto, funcion = opciones[tecla]
        if funcion is None:
            break
        funcion()


def main():
    while True:
        imprimir_titulo("SISTEMA ACADÉMICO")
        print("  1. Estudiantes")
        print("  2. Materias")
        print("  3. Matrículas")
        print("  4. Resumen")
        print("  0. Salir\n")
        tecla = input("Opción: ").strip()
        if tecla == "1":
            ejecutar_menu("ESTUDIANTES", MENU_ESTUDIANTES)
        elif tecla == "2":
            ejecutar_menu("MATERIAS", MENU_MATERIAS)
        elif tecla == "3":
            ejecutar_menu("MATRÍCULAS", MENU_MATRICULAS)
        elif tecla == "4":
            resumen()
        elif tecla == "0":
            imprimir_info("¡Hasta luego! 👋")
            break
        else:
            imprimir_error("Opción no válida")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
