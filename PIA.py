import datetime
import tabulate
import json
import os
import sqlite3
import sys
fecha_hoy = datetime.date.today()
clientes = {}
salas = {}
registros_correctos = []
salas_turnos = []
registros_json = []
def Crear_tablas():
        try:
            with sqlite3.connect("primera.db") as conexion:
                conexion.execute("PRAGMA foreign_keys = ON")
                mi_cursor = conexion.cursor()
                mi_cursor.execute("CREATE TABLE IF NOT EXISTS Salas (clave INTEGER PRIMARY KEY, \
                                nombre TEXT NOT NULL, \
                                cupo INTEGER NOT NULL)")
                mi_cursor.execute("CREATE TABLE IF NOT EXISTS clientes (clave INTEGER PRIMARY KEY, \
                                nombre TEXT NOT NULL, \
                                apellido TEXT NOT NULL)")
                mi_cursor.execute("CREATE TABLE IF NOT EXISTS reservaciones_salas (clave INTEGER PRIMARY KEY, \
                                nombre_evento TEXT NOT NULL, \
                                fecha_reservacion timestamp, \
                                id_Cliente INTEGER NOT NULL, \
                                id_Sala INTEGER NOT NULL, \
                                Turno TEXT NOT NULL, \
                                Estatus TEXT NOT NULL CHECK (Estatus IN ('Activo', 'Cancelado')), \
                                FOREIGN KEY(id_Cliente) REFERENCES Clientes(clave), \
                                FOREIGN KEY(id_Sala) REFERENCES Salas(clave))")
        except sqlite3.Error as e:
            print(e)
        except:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
        finally:
            if conexion:
                conexion.close()
def pedir_texto(mensaje):
    while True:
        texto = input(mensaje).strip()
        if texto == "":
            print("No puede dejar este campo vacío. Intente de nuevo.")
            continue
        if not texto.replace(" ", "").isalpha():
            print("Debe ingresar solo letras. Intente de nuevo.")
            continue
        return texto
def pedir_numero(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor == "":
            print("No puede dejar este campo vacío. Intente de nuevo.")
            continue
        if not valor.isdigit():
            print("Debe ingresar un número válido. Intente de nuevo.")
            continue
        return int(valor)
def pedir_fecha(mensaje):
    while True:
        fecha_str = input(mensaje).strip()
        if fecha_str == "":
            print("No puede dejar la fecha vacía. Intente de nuevo.")
            continue
        try:
            fecha = datetime.datetime.strptime(fecha_str, "%m/%d/%Y").date()
        except ValueError:
            print("Formato de fecha inválido. Use mm/dd/aaaa.")
            continue
        fecha_minima = fecha_hoy + datetime.timedelta(days=2)
        if fecha < fecha_minima:
            print("La fecha debe ser al menos 2 días después de hoy. ")
            continue
        if fecha.weekday() == 6:
            while True:
                Seguro = input("la fecha no puede ser un domingo desea que se mueva para el lunes? S/N ").upper().strip()
                if Seguro == "S":
                    fecha = fecha + datetime.timedelta(days=1)
                    print(f"su reservacion se hara para el dia {fecha.strftime('%m/%d/%Y')}")
                    return fecha
                elif Seguro == "N":
                    print("Favor de ingresar otra fecha que no sea domingo y tiene que ser 2 dias posteriores al actual")
                    break
                else:
                    print("opcion invalida")
                    continue
        return fecha 
def mostrar_menu():
    print("\n===== SISTEMA DE RESERVAS DE COWORKING =====")
    print("1. Registrar reservación de una sala")
    print("2. Editar nombre del evento")
    print("3. Consultar reservaciones")
    print("4. Registrar nuevo cliente")
    print("5. Registrar nueva sala")
    print("6. Cancelar reservacion")
    print("7. Salir")
    print("============================================")
def registrar_cliente():
        try:
            with sqlite3.connect("primera.db") as conexion:
                mi_cursor = conexion.cursor()
                mi_cursor.execute("SELECT MAX(clave) FROM clientes")
                resultado = mi_cursor.fetchone()
                if resultado[0] is None:
                    clave = 1  
                else:
                    clave = resultado[0] + 1
        except sqlite3.Error as e:
            print(f"Error al obtener la última clave: {e}")
            return
    
        nombre = pedir_texto("Ingrese el nombre del cliente: ")
        apellidos = pedir_texto("Ingrese los apellidos del cliente: ")

        clientes[clave] = {"nombre": nombre, "apellidos": apellidos}
        print(f"Cliente registrado con clave {clave}")
        try:
            with sqlite3.connect("primera.db") as conexion:
                mi_cursor = conexion.cursor()
                cliente = clientes[clave]
                mi_cursor.execute("INSERT INTO clientes (nombre, apellido) values(:nombre,:apellidos)" ,cliente)
                conexion.commit()
                print("se han registrado sus datos")
        except sqlite3.Error as e:
            print(e)
        except:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
def registrar_sala():
    try:
        with sqlite3.connect("primera.db") as conexion:
            mi_cursor = conexion.cursor()
            mi_cursor.execute("SELECT MAX(clave) FROM Salas")
            registro = mi_cursor.fetchone()
            if registro[0] is None:
                clave = 1  
            else:
                clave = registro[0] + 1
    except sqlite3.Error as e:
        print(f"Error al obtener la última clave: {e}")
        return
    
    nombre_sala = pedir_texto("Ingrese el nombre de la sala: ")
    cupo = pedir_numero("Ingrese el cupo de la sala: ")


    salas[clave] = {
        "nombre": nombre_sala,
        "cupo": cupo}
    print(f"Sala registrada con clave {clave}")
    try:
        with sqlite3.connect("primera.db") as conexion:
            mi_cursor = conexion.cursor()
            Sala = salas[clave]
            mi_cursor.execute("INSERT INTO Salas (nombre, cupo) values(:nombre,:cupo)" ,Sala)
            conexion.commit()
            print("se han registrado sus datos")
    except sqlite3.Error as e:
        print(e)
    except:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
def Registrar_reservacion_sala():
    global Folio_reservacion
    salas_turnos.clear()
    try:
        with sqlite3.connect("Primera.db") as conexion:
            mi_cursor = conexion.cursor()
            mi_cursor.execute("Select Clave,Nombre,Apellido from clientes ORDER BY Apellido ASC")
            Registros = mi_cursor.fetchall()
            if Registros:
                claves_clientes = [cliente[0] for cliente in Registros]
            else:
                print("No hay clientes registrados")
                return
            while True:
                print(tabulate.tabulate(Registros, headers=["Clave", "Nombre", "Apellidos"]))
                cliente_reservacion = pedir_numero("Ingrese la clave del cliente para la reservación: ")
                if cliente_reservacion in claves_clientes:
                    break
                else:
                    while True:
                        Incorrecto = pedir_texto("la Clave ingresada es inválida desea ingresar otra clave? S/N ").strip().upper()
                        if Incorrecto == "N":   
                            return
                        elif Incorrecto == "S":
                            break
                        else:
                            print("opcion invalida")
    except sqlite3.Error as e:
        print(e)
    except:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
   
    try:
        with sqlite3.connect("primera.db") as conexion:
            mi_cursor = conexion.cursor()
            mi_cursor.execute("Select Clave,Nombre,cupo from salas")
            Registros = mi_cursor.fetchall()
            if not Registros:
                print("No hay registros de salas")
                return
            turnos = ["Matutino","Vespertino","Nocturno"]
            for sala in Registros:
                salas_turnos.append(list(sala) + turnos)
            clave_salas = [sala[0] for sala in salas_turnos]
            print(tabulate.tabulate(salas_turnos, headers = ["Clave", "Nombre" , "Cupo" ,"Turno 1", "Turno 2", "Turno 3"] ))

            while True:
                clave_sala = pedir_numero("Ingrese la clave de la sala deseada: ") 
                if clave_sala in clave_salas:
                    break
                else:
                    print("Esa clave no es de una de las salas favor de elegir otra")
    except sqlite3.Error as e:
        print(e)
    except:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

    fecha_usuario = pedir_fecha("Ingrese la fecha de reservación (mm/dd/aaaa): ")
    fecha_reservacion = fecha_usuario.strftime("%Y-%m-%d")
    Nombre_evento = pedir_texto("Ingrese el nombre del evento: ")
    while True:
        turno = pedir_texto ("Eliga el turno disponible ").capitalize()
        if turno not in turnos:
            print("opcion invalida favor de seleccionar otra")
            continue
        try:
            with sqlite3.connect("primera.db") as conexion:
                mi_cursor = conexion.cursor()
                mi_cursor.execute("SELECT fecha_reservacion,ID_sala,Turno from reservaciones_salas where fecha_reservacion = ? and ID_sala = ? and Turno = ? and Estatus = 'Activo' ", (fecha_reservacion, clave_sala, turno))
                Registros = mi_cursor.fetchall()
                if Registros:
                    while True:
                        opcion = input("Este turno ya está reservado para esta fecha. ¿Desea elegir otro turno? S/N: ").strip().upper()
                        if opcion == "S":
                                break
                        elif opcion == "N":
                            print("Cancelando reservación.")
                            return
                        else:
                            print("opcion invalida")
                else: 
                    break
        except sqlite3.Error as e:
            print(e)
        except:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
    reservaciones[Folio_reservacion] = {
        "nombre_evento": Nombre_evento,
        "fecha_reservacion": fecha_reservacion,
        "id_cliente": cliente_reservacion,
        "id_sala": clave_sala,
        "Turno": turno,
        "Estatus":"Activo"}
    try:
        with sqlite3.connect("primera.db") as conexion:
            mi_cursor = conexion.cursor()
            Reservacion = reservaciones[Folio_reservacion]
            mi_cursor.execute("INSERT INTO reservaciones_salas (nombre_evento, fecha_reservacion, id_cliente, id_sala, Turno, Estatus) values(:nombre_evento,:fecha_reservacion,:id_cliente,:id_sala,:Turno,:Estatus)" ,Reservacion)
            conexion.commit()
            print("se han registrado sus datos")
    except sqlite3.Error as e:
        print(e)
    except:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

    print(f"\nReservación realizada correctamente:")
    print(f"El nombre de su reservacion recien hecha es {Nombre_evento}")
    Folio_reservacion += 1
def consultar_reservaciones_fecha():
    registros_correctos.clear()
    try:
        with sqlite3.connect("primera.db") as conexion:
            mi_cursor = conexion.cursor()
            mi_cursor.execute("select clave from reservaciones_salas")
            registros = mi_cursor.fetchall()
            if not registros:
                print("no hay reservaciones hechas")
                return
    except sqlite3.Error as e:
        print(e)
    except:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")


    while True:
        fecha_consultar = input("Ingrese la fecha a consultar (mm/dd/aaaa): ").strip()
        if not fecha_consultar:
            print("Como no se ingreso fecha se tomara la fecha actual")
            fecha_consultar = datetime.date.today()
            break
        try:
            fecha_consultar = datetime.datetime.strptime(fecha_consultar, "%m/%d/%Y").date()
        except ValueError:
            print("Formato de fecha inválido. Use mm/dd/aaaa.")
            
            continue
        break
    fecha_sql = fecha_consultar.strftime("%Y-%m-%d")
    try:
        with sqlite3.connect("primera.db") as conexion:
            mi_cursor = conexion.cursor()
            mi_cursor.execute("Select r.clave, r.nombre_evento, r.fecha_reservacion, c.Nombre, s.nombre, r.Turno, r.Estatus from reservaciones_salas r " \
                              "join clientes c ON r.id_cliente = c.clave join Salas s on r.id_Sala = s.clave " \
                              "where Estatus = 'Activo' and fecha_reservacion = ?",
                              (fecha_sql,)
                              )
            registros = mi_cursor.fetchall()
            for fila in registros:
                clave, evento, fecha, cliente, sala, turno, Estatus = fila
                fecha_formato_usuario = datetime.datetime.strptime(fecha, "%Y-%m-%d").strftime("%m/%d/%Y")
                registros_correctos.append([clave, evento, fecha_formato_usuario, cliente, sala, turno, Estatus])
            if registros_correctos:
                print(tabulate.tabulate(registros_correctos, headers=["Clave", "Nombre_evento", "fecha_reservacion","id_cliente","id_sala","Turno","Estatus"]))
               
               
                while True:
                    exportar_informacion = pedir_texto("Desea exportar la información a un archivo JSON? S/N: ").upper().strip()
                    if exportar_informacion == "S":
                        with open("exportacion.json", "w", encoding="utf-8" ) as archivo:
                            json.dump(registros_correctos, archivo, indent = 2 , ensure_ascii=False)
                        print("Informacion exportada en un archivo json")
                        return
                    elif exportar_informacion == "N":
                        print("Se le regresara al menu y no se exportara la informacion")
                        return
                    else:
                        print("opcion no valida favor de poner S/n")
            else:
                print("No hay una reservacion para esa fecha en especifico")
                return
    except sqlite3.Error as e:
        print(e)
    except:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
def editar_evento():
    registros_correctos.clear()
    try:
        with sqlite3.connect("primera.db") as conexion:
            mi_cursor = conexion.cursor()
            mi_cursor.execute("select clave from reservaciones_salas")
            registro = mi_cursor.fetchall()
            if not registro:
                print("en estos momentos no hay reservaciones. ")
                return

            while True:
                fecha_inicio_str = input("Ingrese la fecha de inicio del rango (mm/dd/yyyy): ").strip()
                fecha_fin_str = input("Ingrese la fecha de fin del rango (mm/dd/yyyy): ").strip()
                if not fecha_inicio_str or not fecha_fin_str:
                    print("No puede dejar las fechas vacías. Intente de nuevo.")
                    continue
                try:
                    fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, "%m/%d/%Y").date()
                    fecha_fin = datetime.datetime.strptime(fecha_fin_str, "%m/%d/%Y").date()
                except ValueError:
                    print("Formato de fecha inválido. Use mm/dd/yyyy.")
                    continue
                if fecha_inicio > fecha_fin:
                    print("La fecha de inicio no puede ser mayor que la fecha de fin. Intente de nuevo.")
                    continue
                break

            mi_cursor.execute("""
                SELECT r.clave, r.nombre_evento, r.fecha_reservacion, c.nombre, s.nombre
                FROM reservaciones_salas r
                JOIN clientes c ON r.id_cliente = c.clave
                JOIN Salas s ON r.id_sala = s.clave
                WHERE fecha_reservacion BETWEEN ? AND ?
                ORDER BY r.fecha_reservacion
            """, (fecha_inicio, fecha_fin))
            registros = mi_cursor.fetchall()
            if not registros:
                print("No hay reservaciones en ese rango de fechas.")
                return
            for fila in registros:
                clave, evento, fecha, cliente, sala = fila
                fecha_formato_usuario = datetime.datetime.strptime(fecha, "%Y-%m-%d").strftime("%m/%d/%Y")
                registros_correctos.append([clave, evento, fecha_formato_usuario, cliente, sala])

            while True:
                print(tabulate.tabulate(registros_correctos, headers=["Clave", "Nombre evento", "fecha reservacion", "Nombre cliente", "Nombre sala"]))
                seleccion = input("Ingrese el folio de la reservación a editar (X para cancelar): ")
                if seleccion.upper() == "X":
                    print("Operación cancelada.")
                    return
                if not seleccion.isdigit():
                    print("Folio inválido. Intente de nuevo.")
                    continue
                folio_seleccionado = int(seleccion)
                if folio_seleccionado not in [fila[0] for fila in registros]:
                    
                    print("Folio no pertenece a las reservaciones mostradas. Intente de nuevo.")
                    continue
                break

            nuevo_nombre = input("Ingrese el nuevo nombre del evento: ").strip()
            if nuevo_nombre == "":
                print("El nombre no puede estar vacío. Operación cancelada.")
                return

            mi_cursor.execute("UPDATE reservaciones_salas SET nombre_evento = ? WHERE clave = ?", 
                              (nuevo_nombre, folio_seleccionado))
            conexion.commit()
            print(f"Reservación {folio_seleccionado} actualizada con el nuevo nombre: {nuevo_nombre}")

    except sqlite3.Error as e:
        print("Error en la base de datos:", e)
    except Exception as e:
        print("Se produjo un error:", e)
def Cancelar_evento():
    registros_correctos.clear()
    registros_json.clear()
    try:
        with sqlite3.connect("primera.db") as conexion:
            mi_cursor = conexion.cursor()
            mi_cursor.execute("select clave from reservaciones_salas")
            registros = mi_cursor.fetchall()
            if not registros:
                print("no hay reservaciones hechas")
                return
            while True:
                fecha_inicio_str = input("Ingrese la fecha de inicio del rango (mm/dd/yyyy): ").strip()
                fecha_fin_str = input("Ingrese la fecha de fin del rango (mm/dd/yyyy): ").strip()
                if not fecha_inicio_str or not fecha_fin_str:
                    print("No puede dejar las fechas vacías. Intente de nuevo.")
                    continue
                try:
                    fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, "%m/%d/%Y").date()
                    fecha_fin = datetime.datetime.strptime(fecha_fin_str, "%m/%d/%Y").date()
                except ValueError:
                    print("Formato de fecha inválido. Use mm/dd/yyyy.")
                    continue
                if fecha_inicio > fecha_fin:
                    print("La fecha de inicio no puede ser mayor que la fecha de fin. Intente de nuevo.")
                    continue
                break
            mi_cursor.execute("""
                SELECT r.clave, r.nombre_evento, r.fecha_reservacion
                FROM reservaciones_salas r
                JOIN clientes c ON r.id_cliente = c.clave
                JOIN Salas s ON r.id_sala = s.clave
                WHERE fecha_reservacion BETWEEN ? AND ? AND Estatus = 'Activo'
                ORDER BY r.fecha_reservacion
                """, (fecha_inicio, fecha_fin))
            registros = mi_cursor.fetchall()
            if not registros:
                print("No hay reservaciones en ese rango de fechas.")
                return
            for fila in registros:
                clave, evento, fecha = fila
                fecha_formato_usuario = datetime.datetime.strptime(fecha, "%Y-%m-%d").strftime("%m/%d/%Y")
                registros_correctos.append([clave, evento, fecha_formato_usuario])
            while True:
                print(tabulate.tabulate(registros_correctos,headers=("Folio","Nombre evento", "Fecha evento")))
                seleccion = input("Seleccione la clave de la cual cancelara la reservacion  X para cancelar operacion ").strip().upper()
                if seleccion == "X":
                    print("Operación cancelada")
                    return
                elif not seleccion.isdigit():
                    print("Debe ingresar un número válido")
                    continue
                seleccion = int(seleccion)
                if seleccion in [fila[0] for fila in registros_correctos]:
                    fecha_reservacion = [fila[2] for fila in registros_correctos if seleccion == fila[0]]
                    fecha_reservacion = fecha_reservacion[0]
                    fecha_reservacion = datetime.datetime.strptime(fecha_reservacion,"%m/%d/%Y").date()
                    fecha_minima = fecha_hoy + datetime.timedelta(days=2) 
                    if fecha_reservacion < fecha_minima:
                        print("Solo se puede cancelar una reservacion con al menos 2 dias de anticipacion ")
                        return
                    else:
                        while True:
                            cancelar = input("Seguro de querer cancelar la reservacion?  S/N ").upper().strip()
                            if cancelar == "S":
                                mi_cursor.execute("UPDATE reservaciones_salas SET Estatus = 'Cancelado' where Clave = ?", (seleccion,))
                                print("Se ah cancelado su reservacion exitosamente")
                                conexion.commit()
                                if os.path.exists("exportacion.json"):
                                    mi_cursor.execute("Select r.clave, r.nombre_evento, r.fecha_reservacion, c.Nombre, s.nombre, r.Turno, r.Estatus from reservaciones_salas r " \
                                    "join clientes c ON r.id_cliente = c.clave join Salas s on r.id_Sala = s.clave " \
                                    "where Estatus = 'Activo'")
                                    registros = mi_cursor.fetchall()
                                    for fila in registros:
                                        clave, evento, fecha, cliente, sala, turno, Estatus = fila
                                        fecha_formato_usuario = datetime.datetime.strptime(fecha, "%Y-%m-%d").strftime("%m/%d/%Y")
                                        registros_json.append([clave, evento, fecha_formato_usuario, cliente, sala, turno, Estatus])
                                    with open("exportacion.json", "w", encoding="utf-8" ) as archivo:
                                        json.dump(registros_json, archivo, indent = 2 , ensure_ascii=False)
                                return
                            elif cancelar == "N":
                                print("Operacion cancelada regresando al menu... ")
                                return
                            else:
                                print("Seleccione una opcion valida ")
    except sqlite3.Error as e:
        print(e)
    except:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
def main(): 
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()
        if opcion == "1":
            Registrar_reservacion_sala()
        elif opcion == "2":
            editar_evento()
        elif opcion == "3":
            consultar_reservaciones_fecha()
        elif opcion == "4":
            registrar_cliente()
        elif opcion == "5":
            registrar_sala()
        elif opcion == "6":
            Cancelar_evento()
        elif opcion == "7":
            while True:
                seguro = pedir_texto("esta seguro de salir del sistema? S/N ").upper()
                if seguro == "S":
                    exit()
                elif seguro == "N": 
                    print("Regresando al menu ")
                    break
                else:
                    print("Opción no válida. Por favor ingrese 'S' o 'N'. ")
        else:
            print("Opción inválida. Intente nuevamente.")
if os.path.exists("exportacion.json"):
    with open("exportacion.json", "r", encoding="utf-8") as archivo_reservaciones:
        reservaciones_cargadas = json.load(archivo_reservaciones)
        

        reservaciones = {
            dato[0]: {  
                "nombre_evento": dato[1],
                "fecha_reservacion": datetime.datetime.strptime(dato[2], "%m/%d/%Y").date(),
                "cliente": dato[3],
                "sala": dato[4],
                "turno": dato[5],
                "Estatus": dato[6]
            }
            for dato in reservaciones_cargadas
        }

        Folio_reservacion = max(reservaciones.keys(), default=0) + 1

    print("se ha recuperado la versión anterior de la solucion.")
else:
    print("No se ha encontrado una versión anterior, se empezará con un estado inicial vacío.")
    reservaciones = {}
    Folio_reservacion = 1
Crear_tablas()

if __name__ == "__main__":

    main()
