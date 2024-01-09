from conexion import conectar_mysql
import mysql.connector
import tkinter as tk 
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from tkinter import messagebox
from tkinter import Toplevel, Label
import tkinter.font as tkFont
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

#/////////////////////////////




#////////////////////////////
def buscar_identificacion(entry_identificacion):
    identificacion = entry_identificacion.get()
    driver = None
    
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)
        driver.get("https://www.rues.org.co/RM")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "txtSearchNIT")))

        input_identificacion = driver.find_element(By.ID, "txtSearchNIT")
        input_identificacion.clear()
        input_identificacion.send_keys(identificacion)

        driver.find_element(By.ID, "btnConsultaNIT").click()

        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//table[@id='rmTable2']//tbody//td")))

        table_html = driver.find_element(By.ID, "rmTable2").get_attribute("outerHTML")
        soup = BeautifulSoup(table_html, 'html.parser')

        tbody = soup.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')

            data = ""
            for row in rows:
                data_cells = row.find_all('td')
                if data_cells:
                    for column, cell in zip(["Razon Social ó Nombre", "Sigla", "NIT o Núm Id.", "Estado", "Cámara de Comercio", "Matrícula", "Organización Jurídica", "Categoría"], data_cells):
                        data += f"{column}: {cell.text.strip()}\n"
                    data += "\n---\n"
            
            messagebox.showinfo("Información de la empresa", data)

    except TimeoutException:
        messagebox.showerror("Error", "Tiempo de espera agotado. La página puede haber tardado demasiado en cargar.")
    except NoSuchElementException as e:
        messagebox.showerror("Error", f"No se pudo encontrar el elemento: {type(e).__name__} - {str(e)}")
    except WebDriverException as e:
        messagebox.showerror("Error", f"Excepción del WebDriver: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Ha ocurrido un error en la búsqueda: {type(e).__name__} - {str(e)}")

    finally:
        if driver:

            driver.quit()
#///////////////////////////





def consultar_rut_con_selenium_headless(entry_identificacion):
    """
    The function `consultar_rut_con_selenium_headless()` is a Python function that uses Selenium to
    scrape information from a website and store it in a MySQL database.
    :return: The function `consultar_rut_con_selenium_headless()` does not explicitly return any value.
    It performs various actions such as scraping data from a website, inserting data into a MySQL
    database, and displaying information in message boxes.
    """
    identificacion = entry_identificacion.get()
    identificacion_limpia = limpiar_identificacion(identificacion)

    if not identificacion_limpia:
        messagebox.showinfo("Error", "Por favor, ingrese una identificación.")
        return
    # Configuración para ejecutar en modo headless
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Habilitar el modo headless
    
    try:
        # Iniciar el WebDriver con las opciones configuradas
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://muisca.dian.gov.co/WebRutMuisca/DefConsultaEstadoRUT.faces")

        input_identificacion = driver.find_element(By.ID, "vistaConsultaEstadoRUT:formConsultaEstadoRUT:numNit")
        input_identificacion.send_keys(identificacion_limpia)

        boton_buscar = driver.find_element(By.ID, "vistaConsultaEstadoRUT:formConsultaEstadoRUT:btnBuscar")
        boton_buscar.click()

        driver.implicitly_wait(10)
        
        try:
            mensaje_error = driver.find_element(By.XPATH, "//font[contains(text(), 'El NIT')]")
            if mensaje_error:
                mensaje_texto = mensaje_error.text
                messagebox.showinfo("Error en la identificación", mensaje_texto)
                driver.quit()  # Terminar la función si se encuentra un mensaje de error
                return
        except NoSuchElementException:
            pass
        razonSocial_element = None
        try:
            razonSocial_element = driver.find_element(By.ID, "vistaConsultaEstadoRUT:formConsultaEstadoRUT:razonSocial")
        except NoSuchElementException:
            pass

        if razonSocial_element:
            numNit_element = driver.find_element(By.ID, "vistaConsultaEstadoRUT:formConsultaEstadoRUT:numNit")
            numNit = numNit_element.get_attribute("value")
            dv = driver.find_element(By.ID, "vistaConsultaEstadoRUT:formConsultaEstadoRUT:dv").text
            razonSocial = razonSocial_element.text
            fecha_actual_element = driver.find_element(By.XPATH, "//td[contains(text(), 'Fecha Actual')]/following-sibling::td[@class='tipoFilaNormalVerde']")
            fecha = fecha_actual_element.text if fecha_actual_element else "Fecha no encontrada"
            estado = driver.find_element(By.ID, "vistaConsultaEstadoRUT:formConsultaEstadoRUT:estado").text

            # messagebox.showinfo("Información obtenida",
            #                     f"ID: {numNit}\nDV: {dv}\nRazón Social: {razonSocial}\nFecha: {fecha}\nEstado: {estado}")

            conn = conectar_mysql()
            cursor = conn.cursor()

            cursor.execute(
            f"INSERT INTO Proveedor (idProveedor, Nombre, Dv, Estado) "
            f"VALUES ('{numNit}', '{razonSocial}', '{dv}', '{estado}') "
            f"ON DUPLICATE KEY UPDATE Nombre = '{razonSocial}', Dv = '{dv}', Estado = ' {estado}'"
            )
            conn.commit()  # Guardar cambios en la base de datos

            # Guardar en la tabla Consulta
            cursor.execute(
            f"INSERT INTO Consulta (Proveedor_idProveedor, FechaConsulta, Proveedor) VALUES ('{numNit}', '{fecha}','{razonSocial}')"
            )
            conn.commit()  # Guardar cambios en la base de datos
           
            messagebox.showinfo("Información obtenida",
                    f"ID: {numNit}\nDV: {dv}\nRazón Social: {razonSocial}\nFecha: {fecha}\nEstado: {estado}")
            
            driver.quit()
        else:
            # Recolectar información adicional
            numNit = driver.find_element(By.ID, "vistaConsultaEstadoRUT:formConsultaEstadoRUT:numNit").get_attribute("value")
            dv = driver.find_element(By.ID, "vistaConsultaEstadoRUT:formConsultaEstadoRUT:dv").text
            
            # Apellidos
            primer_apellido = driver.find_element(By.ID, "vistaConsultaEstadoRUT:formConsultaEstadoRUT:primerApellido").text
            segundo_apellido = driver.find_element(By.ID, "vistaConsultaEstadoRUT:formConsultaEstadoRUT:segundoApellido").text
            apellidos = f"{primer_apellido} {segundo_apellido}"
            
            # Nombres
            primer_nombre = driver.find_element(By.ID, "vistaConsultaEstadoRUT:formConsultaEstadoRUT:primerNombre").text
            otros_nombres = driver.find_element(By.ID, "vistaConsultaEstadoRUT:formConsultaEstadoRUT:otrosNombres").text
            nombres = f"{primer_nombre} {otros_nombres}"
            
            # Fecha
            fecha_actual_element = driver.find_element(By.XPATH, "//td[contains(text(), 'Fecha Actual')]/following-sibling::td[@class='tipoFilaNormalVerde']")
            fecha = fecha_actual_element.text if fecha_actual_element else "Fecha no encontrada"
            #estado
            estado = driver.find_element(By.ID, "vistaConsultaEstadoRUT:formConsultaEstadoRUT:estado").text
            
            messagebox.showinfo("Información  obtenida",
                                f"ID: {numNit}\nDV: {dv}\nApellidos: {apellidos}\nNombres: {nombres}\nFecha: {fecha}\nEstado: {estado}")

            conn = conectar_mysql()
            cursor = conn.cursor()

            # Inserción en la tabla Consulta
            cursor.execute(
            f"INSERT INTO Proveedor (idProveedor, Nombre, Dv, Estado) "
            f"VALUES ('{numNit}', '{apellidos} {nombres}', '{dv}', '{estado}') "
            f"ON DUPLICATE KEY UPDATE Nombre = '{apellidos} {nombres}', Dv = '{dv}', Estado = '{estado}'"
            )
            conn.commit()  # Guardar cambios en la base de datos

            # Guardar en la tabla Consulta
            cursor.execute(
            f"INSERT INTO Consulta (Proveedor_idProveedor, FechaConsulta,Proveedor) VALUES ('{numNit}', '{fecha}','{apellidos} {nombres}')"
            )
            conn.commit()  # Guardar cambios en la base de datos

           
            # messagebox.showinfo("Información adicional obtenida",
            #                 f"ID: {numNit}\nDV: {dv}\nApellidos: {apellidos}\nNombres: {nombres}\nFecha: {fecha}")

    except Exception as e:
        print(f"Error: {e}")



# Funciones de limpieza y visualización de resultados
def limpiar_identificacion(identificacion):
    """
    The function `limpiar_identificacion` removes dots and dashes from an identification number.
    
    :param identificacion: The parameter "identificacion" is a string representing an identification
    number
    :return: the cleaned identification number without any dots or dashes.
    """
    identificacion_limpia = identificacion.replace('.', '').replace('-', '')
    return identificacion_limpia

def ver_consultas_identificacion(entry_identificacion):
    """
    The function `ver_consultas_identificacion()` retrieves and displays consultation records from a
    MySQL database based on a given identification number.
    """
    identificacion = entry_identificacion.get()
    identificacion_limpia = limpiar_identificacion(identificacion)
    
    try:
        conn = conectar_mysql()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Consulta WHERE Proveedor_idProveedor = '{identificacion_limpia}'")
        resultados = cursor.fetchall()
        conn.close()

        if resultados:
            mostrar_resultados(resultados, "Resultados de Consulta")
        else:
            messagebox.showinfo("No hay resultados", "No se encontraron consultas para esta identificación.")
    except mysql.connector.Error as e:
        print(f"Error al conectar a la base de datos: {e}")

#///////////////////
        
#//////////////////        






def ver_info_proveedor(entry_identificacion):
    """
    The function `ver_info_proveedor()` retrieves information about a supplier from a MySQL database
    based on their identification number.
    """
    identificacion = entry_identificacion.get()
    identificacion_limpia = limpiar_identificacion(identificacion)
    
    try:
        conn = conectar_mysql()
        cursor = conn.cursor()
        cursor.execute(f"SELECT idProveedor, Nombre, Dv, Estado FROM Proveedor WHERE idProveedor = '{identificacion_limpia}'")
        resultados = cursor.fetchall()
        conn.close()

        if resultados:
            mostrar_resultados_proveedor(resultados, "Información de Proveedor")
        else:
            messagebox.showinfo("No hay resultados", "No se encontró proveedor para esta identificación.")
    except mysql.connector.Error as e:
        print(f"Error al conectar a la base de datos: {e}")



def mostrar_resultados_proveedor(resultados, title):
    """
    La función `mostrar_resultados_proveedor` crea una nueva ventana y muestra una tabla con los
    resultados de un proveedor.
    
    :param resultados: Una lista de tuplas que contienen los resultados de cada proveedor. Cada tupla
    debe tener cuatro elementos: identificación, nombre del proveedor, DV (cualquier cosa que represente) y estado
    :param title: El parámetro title es una cadena que representa el título de la ventana que se creará
    para mostrar los resultados
    """
    root_resultados = tk.Toplevel()
    root_resultados.title(title)

    columns = ('Identificación', 'Proveedor', 'DV', 'Estado')
    tree = ttk.Treeview(root_resultados, columns=columns, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')
    
    # Obtener el ancho máximo del texto en la columna "Proveedor"
    proveedor_width = max(len(str(resultado[1])) for resultado in resultados)  # Asumiendo que la columna del proveedor es la segunda
    
    # Ajustar el tamaño de la columna "Proveedor"
    tree.column('Proveedor', width=tkFont.Font().measure("W") * proveedor_width)  # "W" es un carácter de ancho aproximado
    
    for resultado in resultados:
        tree.insert('', 'end', values=resultado)

    tree.pack(expand=True, fill='both')
    root_resultados.mainloop()

def mostrar_resultados(resultados, title):
    """
    The function `mostrar_resultados` creates a new window and displays a table with the given results
    and a title.
    
    :param resultados: A list of results to be displayed in the treeview
    :param title: The title parameter is a string that represents the title of the window where the
    results will be displayed
    """
    root_resultados = tk.Toplevel()
    root_resultados.title(title)

    columns = ('Id Consulta', 'Proveedor', 'FechaConsulta', 'Id proveedor')
    tree = ttk.Treeview(root_resultados, columns=columns, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')
    
    # Obtener el ancho máximo del contenido en la columna 'Proveedor'
    max_width_proveedor = max(len(str(row[1])) for row in resultados)  # Considerando que 'Proveedor' es el segundo elemento (índice 1)

    # Establecer un ancho mínimo para la columna 'Proveedor' (puedes ajustar este valor)
    tree.column('Proveedor', width=max_width_proveedor * 10)  # Ajusta el ancho multiplicando por un factor adecuado

    for resultado in resultados:
        tree.insert('', 'end', values=resultado)

    tree.pack(expand=True, fill='both')
    root_resultados.mainloop()

def mostrar_tabla_consultas():
    """
    The function "mostrar_tabla_consultas" retrieves data from a MySQL database table called "Consulta"
    and displays the results.
    """
    try:
        conn = conectar_mysql()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Consulta")
        resultados = cursor.fetchall()
        conn.close()

        if resultados:
            mostrar_resultados(resultados, "Tabla de Consultas")
        else:
            messagebox.showinfo("No hay resultados", "La tabla de Consultas está vacía.")
    except mysql.connector.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
