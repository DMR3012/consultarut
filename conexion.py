import mysql.connector

def conectar_mysql():
    conexion = {
        'user': 'root',
        'host': '127.0.0.1',
        'port': 3306,
        'database': 'consultaestadorues',
    }

    try:
        conn = mysql.connector.connect(**conexion)
        return conn
    except mysql.connector.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
    
