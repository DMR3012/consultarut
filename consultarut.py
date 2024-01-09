import mysql.connector
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import tkinter.font as tkFont
import PIL
from PIL import Image, ImageTk
import selenium
from selenium import webdriver
import webbrowser
from conexion import conectar_mysql
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
    

def consultar_rut_con_selenium_headless():
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
            messagebox.showinfo("Información obtenida",
                    f"ID: {numNit}\nDV: {dv}\nRazón Social: {razonSocial}\nFecha: {fecha}\nEstado: {estado}")
            conn = conectar_mysql()
            cursor = conn.cursor()

            cursor.execute(
            f"INSERT INTO Proveedor (idProveedor, Nombre, Dv, Estado) "
            f"VALUES ('{numNit}', '{razonSocial}', '{dv}', '{estado}') "
            f"ON DUPLICATE KEY UPDATE Nombre = '{razonSocial}', Dv = '{dv}', Estado = '{estado}'"
            )
            conn.commit()  # Guardar cambios en la base de datos

            # Guardar en la tabla Consulta
            cursor.execute(
            f"INSERT INTO Consulta (Proveedor_idProveedor, FechaConsulta, Proveedor) VALUES ('{numNit}', '{fecha}','{razonSocial}')"
            )
            conn.commit()  # Guardar cambios en la base de datos

            

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
                                f"ID: {numNit}\nDV: {dv}\nApellidos: {apellidos}\nNombres: {nombres}\nFecha: {fecha}\nEstado{estado}")

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

def ver_consultas_identificacion():
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






def ver_info_proveedor():
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
    root_resultados = tk.Toplevel()
    root_resultados.title(title)

    frame = ttk.Frame(root_resultados)
    frame.pack(expand=True, fill='both', padx=5, pady=5)

    columns = ('Identificación', 'Proveedor', 'DV', 'Estado')
    tree = ttk.Treeview(frame, columns=columns, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')
    
    proveedor_width = max(len(str(resultado[1])) for resultado in resultados)
    tree.column('Proveedor', width=tkFont.Font().measure("W") * proveedor_width)
    
    for resultado in resultados:
        tree.insert('', 'end', values=resultado)

    tree.pack(expand=True, fill='both', padx=2, pady=2)

    # Aplicar un borde al frame que contiene el Treeview
    frame.config(borderwidth=2, relief="solid")

    root_resultados.mainloop()

def mostrar_resultados(resultados, title):
    root_resultados = tk.Toplevel()
    root_resultados.title(title)

    frame = ttk.Frame(root_resultados)
    frame.pack(expand=True, fill='both', padx=5, pady=5)

    columns = ('Id Consulta', 'Proveedor', 'FechaConsulta', 'Id proveedor')
    tree = ttk.Treeview(frame, columns=columns, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')
    
    max_width_proveedor = max(len(str(row[1])) for row in resultados)
    tree.column('Proveedor', width=max_width_proveedor * 10)

    for resultado in resultados:
        tree.insert('', 'end', values=resultado)

    tree.pack(expand=True, fill='both', padx=2, pady=2)

    # Aplicar un borde al frame que contiene el Treeview
    frame.config(borderwidth=2, relief="solid")

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


#/////////////////
def on_entry_click(event):
    if entry_identificacion.get() == "Ingrese ID":
        entry_identificacion.delete(0, tk.END)
        entry_identificacion.config(fg='black')

def on_focus_out(event):
    if entry_identificacion.get() == "":
        entry_identificacion.insert(0, "Ingrese ID")
        entry_identificacion.config(fg='gray')


root = tk.Tk()
root.title("Consulta Rut")
window_width = 450
window_height = 350

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2

root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
root.resizable(False, False)

label = tk.Label(root, text="Consulta RUT", font=("Onix", 14))
label.pack()

style = ttk.Style()
style.theme_use('clam')

style.configure(
    'Custom.TEntry',
    borderwidth=2,
    relief='flat',
    font=('Onix', 11),
    padding=(5, 5)
)

entry_identificacion = ttk.Entry(root, width=23, style='Custom.TEntry', foreground='gray')
entry_identificacion.insert(0, "Ingrese ID")
entry_identificacion.bind('<FocusIn>', on_entry_click)
entry_identificacion.bind('<FocusOut>', on_focus_out)
entry_identificacion.pack()

style.theme_use("clam")

style.configure("Custom.TButton",
                foreground="white",
                background="gray",
                font=("Onix", 11),
                relief="raised")

boton_ver_consultas = ttk.Button(root, text="Ver Consultas del ID", style="Custom.TButton", command=ver_consultas_identificacion, width=20)
boton_ver_consultas.pack(padx=10, pady=15)

boton_ver_info_proveedor = ttk.Button(root, text="Ver Info de Proveedor", style="Custom.TButton", command=ver_info_proveedor, width=20)
boton_ver_info_proveedor.pack(padx=10, pady=15)

boton_mostrar_tabla = ttk.Button(root, text="Mostrar Tabla Completa", style="Custom.TButton", command=mostrar_tabla_consultas, width=20)
boton_mostrar_tabla.pack(padx=10, pady=15)

boton_consultar_rut_headless = ttk.Button(root, text="Consultar RUT DIAN", style="Custom.TButton", command=consultar_rut_con_selenium_headless, width=20)
boton_consultar_rut_headless.pack(padx=10, pady=15)

# label = tk.Label(root, text="APP EN DESARROLLO", font=("Onix", 21), fg="gray")
# label.pack()

root.mainloop()