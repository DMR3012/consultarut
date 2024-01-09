import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk
from database.database import ejecutar_consulta
from mysql.connector import Error
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def normalizar_nit(nit):
    return nit.replace('.', '').replace('-', '').upper()

def obtener_numero_verificacion(nit):
    # Obtener el número de verificación después del guión
    partes = nit.split('-')
    if len(partes) == 2 and partes[1].isdigit():
        return partes[1]
    else:
        return ''

def consultar_estado_rues(nit):
    try:
        nit_transformado = normalizar_nit(nit)
        resultados, nit = integrar_selenium_consulta(nit_transformado)

        # Verificar el resultado de la consulta
        if not resultados:
            # Caso 1: Documento no registrado en el RUT
            messagebox.showinfo("Alerta", f"Consulta Inválida: {nit} no se encuentra registrado en el RUT.")
            return

        # Obtener información de la consulta
        datos_proveedor = resultados[0]

        # Obtener el número de verificación
        numero_verificacion = obtener_numero_verificacion(nit_transformado)

        # Formatear el NIT para visualización en la tabla de consultas
        nit_formateado = f"{nit_transformado[:-1]}-{nit_transformado[-1]}" if '-' not in nit_transformado else nit_transformado

        # Insertar en la tabla de consultas
        guardar_historial(nit_formateado)

        # Verificar si el proveedor existe en la base de datos
        proveedor_existente = consultar_proveedor_en_db(nit_transformado)

        if proveedor_existente:
            # Caso 2: Documento existe en la tabla y se espera cambio de información
            if proveedor_existente['ActividadEconomica'] != datos_proveedor['Categoría']:
                messagebox.showwarning("Alerta", "¡Alerta! Hubo un cambio en la actividad económica del proveedor.")

            # Actualizar información en la tabla de proveedores
            actualizar_proveedor_en_db(nit_transformado, datos_proveedor, numero_verificacion)
        else:
            # Caso 3: Documento no existe en la tabla y se espera crear un nuevo proveedor
            messagebox.showinfo("Alerta", "¡Alerta! Documento no existe en la tabla y se espera crear un nuevo proveedor.")
            # Insertar nuevo proveedor en la tabla de proveedores
            insertar_proveedor_en_db(nit_transformado, datos_proveedor)

        # Mostrar mensaje de éxito en la terminal
        print("Consulta Finalizada RUT Activo" if datos_proveedor['Estado'] == 'Activo'
              else "Consulta Finalizada RUT Inactivo")

        # Caso 4: Documento existe en la tabla y debería generar alerta por cambio de actividad económica
        if proveedor_existente and proveedor_existente['ActividadEconomica'] != datos_proveedor['Categoría']:
            messagebox.showwarning("Alerta", "¡Alerta! Hubo un cambio en la actividad económica del proveedor.")

        # Limpiar datos existentes en la tabla principal
        for row in empresa_tree.get_children():
            empresa_tree.delete(row)

        # Mostrar información de la empresa en la tabla principal
        empresa_tree.insert('', 'end', values=(
            datos_proveedor['Razon Social ó Nombre'],
            datos_proveedor['NIT o Núm Id.'].split('-')[0],  # Mostrar solo la parte antes del guión en la columna Nit
            datos_proveedor['Estado'],
            datos_proveedor['Cámara de Comercio'],
            datos_proveedor['Matrícula'],
            datos_proveedor['Organización Jurídica'],
            datos_proveedor['Categoría'],
        ))

        # Mostrar la tabla principal
        empresa_tree.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        empresa_tree.lift()

        # Actualizar el estado de las variables
        consulta_visible.set(True)
        historial_visible.set(False)

    except Exception as e:
        # Mostrar mensaje de error en la terminal
        print(f"Se produjo un error al consultar el RUES: {str(e)}")
        # Caso general: Mostrar mensaje de error
        messagebox.showerror("Error", f"Se produjo un error al consultar el RUES: {str(e)}")


def consultar_proveedor_en_db(nit):
    # Función para consultar un proveedor en la base de datos
    query = f"SELECT * FROM proveedor WHERE ProvNit = '{nit}'"
    resultado = ejecutar_consulta(query)
    return resultado[0] if resultado else None

def insertar_proveedor_en_db(nit, datos_proveedor):
    try:
        # Función para insertar o actualizar un proveedor en la base de datos
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Verificar si el proveedor ya existe en la base de datos
        proveedor_existente = consultar_proveedor_en_db(nit)

        if proveedor_existente:
            # Proveedor existente, actualizar la información
            query = (
                f"UPDATE proveedor SET ProvNombre = '{datos_proveedor['Razon Social ó Nombre']}', "
                f"FechaUltimaActualizacion = '{fecha_actual}', Estado = '{datos_proveedor['Estado']}', "
                f"CamaraComercio = '{datos_proveedor['Cámara de Comercio']}', "
                f"Matricula = '{datos_proveedor['Matrícula']}', "
                f"OrganizacionJuridica = '{datos_proveedor['Organización Jurídica']}', "
                f"Categoria = '{datos_proveedor['Categoría']}' "
                f"WHERE ProvNit = '{nit}'"
            )
        else:
            # Proveedor no existente, insertar nuevos datos
            query = (
                f"INSERT INTO proveedor (ProvNit, ProvNombre, FechaRegistro, FechaUltimaActualizacion, Estado, "
                f"CamaraComercio, Matricula, OrganizacionJuridica, Categoria) "
                f"VALUES ('{nit}', '{datos_proveedor['Razon Social ó Nombre']}', '{fecha_actual}', '{fecha_actual}', "
                f"'{datos_proveedor['Estado']}', '{datos_proveedor['Cámara de Comercio']}', "
                f"'{datos_proveedor['Matrícula']}', '{datos_proveedor['Organización Jurídica']}', '{datos_proveedor['Categoría']}')"
            )

        # Ejecutar la consulta
        ejecutar_consulta(query)

        # Mostrar mensaje de éxito en la terminal
        if proveedor_existente:
            print("Información actualizada en la base de datos.")
        else:
            print("Datos insertados correctamente en la base de datos.")

    except Error as e:
        # Mostrar mensaje de error en la terminal
        print(f"Error al insertar/actualizar datos en la base de datos: {str(e)}")


def actualizar_proveedor_en_db(nit, datos_proveedor):
    try:
        # Obtener la fecha y hora actuales
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Actualizar la información de proveedor en la base de datos
        query = f"UPDATE proveedor SET ProvNombre = '{datos_proveedor['Razon Social ó Nombre']}', " \
                f"FechaUltimaActualizacion = '{fecha_actual}', Estado = '{datos_proveedor['Estado']}', " \
                f" = '{datos_proveedor['']}', CamaraComercio = '{datos_proveedor['Cámara de Comercio']}', " \
                f"Matricula = '{datos_proveedor['Matrícula']}', " \
                f"OrganizacionJuridica = '{datos_proveedor['Organización Jurídica']}' " \
                f"WHERE ProvNit = '{nit}'"
        ejecutar_consulta(query)

        # Mostrar mensaje de éxito en la terminal
        print("Datos actualizados correctamente en la base de datos.")

    except Error as e:
        # Mostrar mensaje de error en la terminal
        print(f"Error al actualizar datos en la base de datos: {str(e)}")

def integrar_selenium_consulta(nit):
    driver = None
    resultados = []

    try:
        # Configuración del navegador Chrome
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")

        # Inicializar el navegador
        driver = webdriver.Chrome(options=options)
        # Abrir la página del RUES
        driver.get("https://www.rues.org.co/RM")

        print("Esperando a que el campo de búsqueda esté presente...")
        # Esperar a que el campo de búsqueda esté presente
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "txtSearchNIT")))
        print("Campo de búsqueda encontrado.")

        # Encontrar el campo de texto y escribir la identificación
        input_identificacion = driver.find_element(By.ID, "txtSearchNIT")
        input_identificacion.clear()
        input_identificacion.send_keys(nit)

        # En este caso, estamos haciendo clic en el botón usando el ID
        driver.find_element(By.ID, "btnConsultaNIT").click()

        print("Esperando a que la tabla tenga contenido...")
        # Esperar a que la tabla tenga contenido (puedes ajustar el tiempo según la carga de la tabla)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//table[@id='rmTable2']//tbody//td"))
        )
        print("Tabla tiene contenido.")

        # Dormir para dar tiempo a la carga completa de la tabla
        time.sleep(2)

        # Obtener el contenido HTML de la tabla
        table_html = driver.find_element(By.ID, "rmTable2").get_attribute("outerHTML")

        # Utilizar BeautifulSoup para analizar el HTML
        soup = BeautifulSoup(table_html, 'html.parser')

        # Encontrar el encabezado (thead)
        thead = soup.find('thead')
        if thead:
            # Encontrar todas las filas en el encabezado
            header_rows = thead.find_all('tr')

            # Obtener los nombres de las columnas
            headers = [th.text.strip() for th in header_rows[-1].find_all('th')]

            # Encontrar el cuerpo de la tabla (tbody)
            tbody = soup.find('tbody')
            if tbody:
                # Encontrar todas las filas en el cuerpo
                rows = tbody.find_all('tr')

                # Procesar cada fila y mostrar la información
                for row in rows:
                    celdas = row.find_all('td')

                    # Verificar si la longitud de headers y celdas coincide
                    if len(headers) == len(celdas):
                        # Encabezados que aparecen con más frecuencia en 
                        data = {headers[i]: celdas[i].text.strip() for i in range(len(headers))}
                        resultados.append(data)

                        # Mostrar información de la empresa
                        print("Información de la empresa:")
                        for column, value in data.items():
                            print(f"{column}: {value}")
                        print("\n---\n")
                    else:
                        print("La longitud de headers y celdas no coincide.")

        print("Datos extraídos exitosamente.")

    except TimeoutException:
        print("Tiempo de espera agotado. La página puede haber tardado demasiado en cargar.")
    except NoSuchElementException as e:
        print(f"No se pudo encontrar el elemento: {type(e).__name__} - {str(e)}")
    except WebDriverException as e:
        print(f"Excepción del WebDriver: {str(e)}")
    except Exception as e:
        print(f"Ha ocurrido un error en la búsqueda: {type(e).__name__} - {str(e)}")

    finally:
        # Este bloque finally asegura que el navegador se cierre incluso si ocurre un error
        if driver:
            driver.quit()

    return resultados, nit


def obtener_historial():
    try:
        query = "SELECT Consultas.idConsulta, Consultas.FechaConsulta, Proveedor.ProvNit, Proveedor.ProvNombre FROM Consultas JOIN Proveedor ON Consultas.proveedorNit = Proveedor.ProvNit ORDER BY Consultas.FechaConsulta DESC"
        historial = ejecutar_consulta(query)
        return historial
    except Exception as e:
        messagebox.showerror("Error", f"Se produjo un error al obtener el historial: {str(e)}")


def consultar_historial():
    try:
        # Ocultar la tabla principal
        empresa_tree.grid_forget()

        # Limpiar datos existentes en la tabla de historial
        for row in historial_tree.get_children():
            historial_tree.delete(row)

        # Obtener historial de consultas
        historial = obtener_historial()

        # Mostrar todos los resultados en la tabla de historial
        for consulta in historial:
            historial_tree.insert('', 'end', values=(consulta[0], consulta[1], consulta[2], consulta[3]))

        # Mostrar la tabla de historial
        historial_tree.grid(row=3, column=0, columnspan=4, padx=40, pady=30, sticky="nsew")
        historial_tree.lift()

        # Actualizar el estado de las variables
        consulta_visible.set(False)
        historial_visible.set(True)

    except Exception as e:
        messagebox.showerror("Error", f"Se produjo un error al consultar el historial: {str(e)}")


def guardar_historial(nit):
    try:
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insertar en la tabla de consultas
        query = f"INSERT INTO consultas (proveedorNit, FechaConsulta) VALUES ('{nit}', '{fecha_hora}')"
        ejecutar_consulta(query)
    except Error as e:
        # Mostrar mensaje de error en la terminal
        print(f"Error al guardar el historial: {str(e)}")


def on_window_resize(event):
    screen_width = root.winfo_width()
    screen_height = root.winfo_height()

    resized_image = background_image.resize((screen_width, screen_height), Image.BICUBIC)
    background_photo = ImageTk.PhotoImage(resized_image)

    canvas.itemconfig(background_canvas, image=background_photo)
    canvas.image = background_photo

    if consulta_visible.get():
        empresa_tree.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        empresa_tree.lift()
    elif historial_visible.get():
        historial_tree.grid(row=3, column=0, columnspan=4, padx=40, pady=30, sticky="nsew")
        historial_tree.lift()

# Crear la ventana principal
root = tk.Tk()
root.title("Consulta de Empresa")

# Configuración del fondo de la ventana
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

background_image = Image.open("./images/background.jpg")
resized_image = background_image.resize((screen_width, screen_height), Image.BICUBIC)
background_photo = ImageTk.PhotoImage(resized_image)

canvas = tk.Canvas(root)
canvas.grid(row=0, column=0, rowspan=7, columnspan=7, sticky="nsew")

background_canvas = canvas.create_image(0, 0, anchor=tk.NW, image=background_photo)

nit_label = ttk.Label(root, text="NIT:")
nit_entry = ttk.Entry(root, font=("Times new Roman", 12))
consultar_button = ttk.Button(root, text="Consultar", command=lambda: consultar_estado_rues(nit_entry.get()))
historial_button = ttk.Button(root, text="Historial de Consultas", command=consultar_historial)

empresa_tree = ttk.Treeview(root, columns=("Razon Social ó Nombre", "NIT o Núm Id", "Estado", "Cámara de Comercio", "Matrícula", "Organización Jurídica", "Categoría"), show="headings", height=5)
empresa_tree.heading("Razon Social ó Nombre", text="Razon Social ó Nombre")
empresa_tree.heading("NIT o Núm Id", text="NIT o Núm Id")
empresa_tree.heading("Estado", text="Estado")
empresa_tree.heading("Cámara de Comercio", text="Cámara de Comercio")
empresa_tree.heading("Matrícula", text="Matrícula")
empresa_tree.heading("Organización Jurídica", text="Organización Jurídica")
empresa_tree.heading("Categoría", text="Categoría")

empresa_tree.heading("#0", anchor="center")
for col in empresa_tree["columns"]:
    empresa_tree.heading(col, anchor="center")

empresa_tree.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
historial_tree = ttk.Treeview(root, columns=("Id Consulta", "Fecha y Hora", "NIT", "Nombre"), show="headings", height=5)
historial_tree.heading("Id Consulta", text="Id Consulta")
historial_tree.heading("Fecha y Hora", text="Fecha y Hora")
historial_tree.heading("NIT", text="NIT")
historial_tree.heading("Nombre", text="Nombre")

for col in historial_tree["columns"]:
    historial_tree.column(col, anchor="center")
    historial_tree.column(col, width=150)

historial_tree.heading("#0", anchor="center")
for col in historial_tree["columns"]:
    historial_tree.heading(col, anchor="center")

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(6, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(6, weight=1)

nit_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)
nit_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
consultar_button.grid(row=1, column=2, padx=10, pady=10, sticky=tk.W)
historial_button.grid(row=1, column=3, padx=10, pady=10, sticky=tk.W)

consulta_visible = tk.BooleanVar()
historial_visible = tk.BooleanVar()
consulta_visible.set(True)
historial_visible.set(False)

empresa_tree.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

root.bind('<Configure>', on_window_resize)

root.mainloop()