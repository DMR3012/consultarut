import tkinter as tk
from tkinter import ttk
from funciones import (
    ver_consultas_identificacion,
    ver_info_proveedor,
    mostrar_tabla_consultas,
    consultar_rut_con_selenium_headless,
    buscar_identificacion,
    
)
#////////////////////////

import tkinter as tk
from tkinter import ttk

# Definición de funciones y GUI aquí...


import tkinter as tk
from tkinter import ttk
from funciones import (
    ver_consultas_identificacion,
    ver_info_proveedor,
    mostrar_tabla_consultas,
    consultar_rut_con_selenium_headless,
    buscar_identificacion,
)


def on_entry_click(event):
    if entry_identificacion.get() == "Ingrese ID":
        entry_identificacion.delete(0, tk.END)
        entry_identificacion.config(fg='black')

def on_focus_out(event):
    if entry_identificacion.get() == "":
        entry_identificacion.insert(0, "Ingrese ID")
        entry_identificacion.config(fg='gray')

def validar_input(new_value):
    return new_value.isdigit() or new_value == ""

root = tk.Tk()
root.title("Consulta Rut")
window_width = 550
window_height = 450

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2

root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
root.resizable(False, False)

label = tk.Label(root, text="Consulta RUT sin DV", font=("Onix", 14))
label.pack()


# The code you provided is creating a graphical user interface (GUI) using the tkinter library in
# Python. Here is a breakdown of what each part of the code does:
style = ttk.Style()
style.theme_use('clam')

style.configure(
    'Custom.TEntry',
    borderwidth=2,
    relief='flat',
    font=('Onix', 11),
    padding=(5, 5)
)

validate_cmd = root.register(validar_input)
entry_identificacion = ttk.Entry(root, width=23, style='Custom.TEntry', foreground='gray', validate="key", validatecommand=(validate_cmd, '%P'))
entry_identificacion.insert(0, "Ingrese ID sin DV")
entry_identificacion.bind('<FocusIn>', on_entry_click)
entry_identificacion.bind('<FocusOut>', on_focus_out)
entry_identificacion.pack()

style.theme_use("clam")

style.configure("Custom.TButton",
                foreground="white",
                background="gray",
                font=("Onix", 11),
                relief="raised")

boton_ver_consultas = ttk.Button(root, text="Ver Consultas del ID", style="Custom.TButton", command=lambda: ver_consultas_identificacion (entry_identificacion), width=20)
boton_ver_consultas.pack(padx=10, pady=15)

boton_ver_info_proveedor = ttk.Button(root, text="Ver Info de Proveedor", style="Custom.TButton", command=lambda: ver_info_proveedor(entry_identificacion), width=20)
boton_ver_info_proveedor.pack(padx=10, pady=15)

boton_mostrar_tabla = ttk.Button(root, text="Mostrar Tabla Completa", style="Custom.TButton", command=mostrar_tabla_consultas, width=20)
boton_mostrar_tabla.pack(padx=10, pady=15)

boton_consultar_rut_headless = ttk.Button(root, text="Consultar RUT DIAN", style="Custom.TButton", command=lambda: consultar_rut_con_selenium_headless(entry_identificacion), width=20)
boton_consultar_rut_headless.pack(padx=10, pady=15)


boton_consultar_rut_headless = ttk.Button(root, text="Consultar RUES  DIAN", style="Custom.TButton", command=lambda: buscar_identificacion(entry_identificacion), width=20)
boton_consultar_rut_headless.pack(padx=10, pady=15)




# label = tk.Label(root, text="APP EN DESARROLLO", font=("Onix", 21), fg="gray")
# label.pack()

root.mainloop()
