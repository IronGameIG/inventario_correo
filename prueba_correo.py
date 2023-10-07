import tkinter as tk
from tkinter import messagebox
import sqlite3

#----------
#generar reporte
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime
#---------

#---------------
#enviar reporte por correo
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
#--------------------------------------




#-------------------------------------
#VARIABLES
codigo_seleccionado = None
codigo_seleccionado_stock = None



#-------------------------------------

#--------------------------------------------------------------
#CREAR LA BASE DE DATOS
def crear_db():
    conn = sqlite3.connect("Inventario.db")
    cursor = conn.cursor()
    cursor.execute(
    '''CREATE TABLE IF NOT EXISTS existencias (
            Codigo INTEGER PRIMARY KEY,
            Nombre TEXT,
            Detalle TEXT,
            Stock INTEGER)''')
    conn.commit()
    conn.close()
#--------------------------------------------------------------

#------------------------------------
#LIMPIAR CAMPOS
def limpiar_campos_general():
    entry_nombre.delete(0,tk.END)
    entry_detalle.delete(0,tk.END)
    entry_stock.delete(0,tk.END)
    #entry_codigo.delete(0, tk.END)
#-------------------------------------

#--------------------------------------------------------------
#ACTUALIZAR LISTA
def actualizar_lista():

    listbox.delete(0, tk.END)   
    conn = sqlite3.connect("Inventario.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, detalle, stock,  codigo FROM existencias")
    existencias = cursor.fetchall()
    conn.close()

    for existencias in existencias:
        listbox.insert(tk.END, f"Nombre: {existencias[0]} | Detalle: {existencias[1]} | Stock: {existencias[2]} | " 
                       f"Código: {existencias[3]}")
#----------------------------------------------------------------

#----------------------------------------------------------------
#ACTUALIZAR LISTA STOCK
def actualizar_lista_stock():

    listbox_stock.delete(0, tk.END)   
    conn = sqlite3.connect("Inventario.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, detalle, stock,  codigo FROM existencias")
    existencias = cursor.fetchall()
    conn.close()

    for existencias in existencias:
        listbox_stock.insert(tk.END, f"Nombre: {existencias[0]} | Detalle: {existencias[1]} | Stock: {existencias[2]} | " 
                       f"Código: {existencias[3]}")
#---------------------------------------------------------

#-------------------------------------------------------------
#CREAR FUNCION AGREGAR PRODUCTO
def agregar_producto():
    
    nombre = entry_nombre.get()
    detalle = entry_detalle.get()
    stock = entry_stock.get()

    if nombre and detalle and stock:
        conn = sqlite3.connect("Inventario.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO existencias (Nombre, Detalle, Stock) VALUES (?,?,?)",
                    (nombre, detalle, stock))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Producto agregado con éxito!")
        limpiar_campos_general() 
        entry_nombre.focus_set()
        actualizar_lista()


    else:
        messagebox.showerror("Error", "Producto no agregado, favor de completar campos.")
#-----------------------------------------------------------

#--------------------------------------------------------
#CREAR FUNCION EDITAR STOCK
def editar_stock_producto_seleccionado(operacion):
    global codigo_seleccionado_stock
    if codigo_seleccionado_stock is not None:
        cantidad = entry_stock.get()
        if cantidad:
            conn = sqlite3.connect("Inventario.db")
            cursor = conn.cursor()
            cursor.execute("SELECT Stock FROM existencias WHERE Codigo=?", (codigo_seleccionado_stock,))
            resultado = cursor.fetchone()
            
            if resultado:
                stock_actual = resultado[0]
                try:
                    cantidad = int(cantidad)
                    if operacion == "agregar":
                        nuevo_stock = stock_actual + cantidad  # Agregar la cantidad ingresada
                    elif operacion == "quitar":
                        nuevo_stock = stock_actual - cantidad  # Restar la cantidad ingresada

                    if nuevo_stock >= 0:
                        cursor.execute("UPDATE existencias SET Stock=? WHERE Codigo=?", (nuevo_stock, codigo_seleccionado_stock))
                        conn.commit()
                        conn.close()
                        messagebox.showinfo("Éxito", f"Stock actualizado: {nuevo_stock}")
                        actualizar_lista_stock()
                        actualizar_lista()
                        entry_stock.delete(0, tk.END)  # Limpiar el campo de entrada de stock
                    else:
                        messagebox.showerror("Error", "No puede tener un stock negativo.")
                        entry_stock.delete(0, tk.END)
                except ValueError:
                    messagebox.showerror("Error", "La cantidad debe ser un número entero.")
                    entry_stock.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Producto no encontrado.")
        else:
            messagebox.showerror("Error", "Ingrese una cantidad.")

#-----------------------------------------------------------

#-------------------------------------------------------------
#CREAR FUNCION ELIMINAR PRODUCTO SELECCIONADO
def eliminar_producto_seleccionado():
    if codigo_seleccionado is not None:
        conn = sqlite3.connect("Inventario.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM existencias WHERE Codigo=?", (codigo_seleccionado,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Producto eliminado con éxito.")
        actualizar_lista()
#--------------------------------------------------------------

#----------------------------------------------------------------
#FUNCION PARA MANEJAR LA SELECCION EN LA LISTA
def seleccionar_producto(event):
    global codigo_seleccionado, codigo_seleccionado_stock
    seleccion = listbox.curselection()
    if seleccion:
        codigo_seleccionado = int(listbox.get(seleccion[0]).split("Código: ")[1])
#--------------------------------------------------------------------

#--------------------------------------------------------------------
#FUNCION PARA MANEJAR LA SELECCION EN LA LISTA DEL STOCK
def seleccionar_producto_stock(event):
    global codigo_seleccionado_stock
    seleccion = listbox_stock.curselection()
    if seleccion:
        codigo_seleccionado_stock = int(listbox_stock.get(seleccion[0]).split("Código: ")[1])

#--------------------------------------------------------------------
#CREAR FUNCION FILTRAR PRODUCTOS POR NOMBRE INICIO PANTALLA INICIAL
def filtro():
    filtro = entry_filtro.get()

    listbox.delete(0, tk.END)
    conn = sqlite3.connect("Inventario.db")
    cursor = conn.cursor()

    # Utiliza una consulta SQL para filtrar los productos por nombre
    cursor.execute("SELECT nombre, detalle, stock, codigo FROM existencias WHERE nombre LIKE ?",
                   ('%' + filtro + '%',))  # Usamos % para buscar nombres que contengan el filtro

    existencias = cursor.fetchall()
    conn.close()

    for existencia in existencias:
        listbox.insert(tk.END, f"Nombre: {existencia[0]} | Detalle: {existencia[1]} | Stock: {existencia[2]} | Código: {existencia[3]}")
#--------------------------------------------------------------------

#---------------------------------------------------------------------------
#CREAR FUNCION FILTRAR PRODUCTOS POR NOMBRE INICIO PANTALLA STOCK
def filtro_stock():
    filtro = entry_filtro_stock.get()

    listbox_stock.delete(0, tk.END)
    conn = sqlite3.connect("Inventario.db")
    cursor = conn.cursor()

    # Utiliza una consulta SQL para filtrar los productos por nombre
    cursor.execute("SELECT nombre, detalle, stock, codigo FROM existencias WHERE nombre LIKE ?",
                   ('%' + filtro + '%',))  # Usamos % para buscar nombres que contengan el filtro

    existencias = cursor.fetchall()
    conn.close()

    for existencia in existencias:
            listbox_stock.insert(tk.END, f"nombre: {existencia[0]} | detalle: {existencia[1]} | stock: {existencia[2]} | codigo: {existencia[3]}")
#------------------------------------------------------------------------

#--------------------------------------------------
#CREAR FUNCION DE GENERAR REPORTE DE PRODUCTOS
def generar_informe_pdf():
    # Obtén la fecha actual
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")

    # Crea un archivo PDF
    pdf_filename = f"Informe_Productos_{fecha_actual}.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    # Agrega el nombre de la empresa y la fecha
    c.drawString(100, 750, "Nombre de la Empresa: [AISLAHOME]")
    c.drawString(100, 730, f"Fecha del Informe: {fecha_actual}")
    c.drawString(100, 710, "-" * 50)

    # Conecta a la base de datos y obtén los productos
    conn = sqlite3.connect("Inventario.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Nombre, Detalle, Stock FROM existencias")
    productos = cursor.fetchall()
    conn.close()

    # Agrega la lista de productos al informe
    y = 680
    for producto in productos:
        nombre, detalle, stock = producto
        y -= 20
        c.drawString(100, y, f"Nombre: {nombre}")
        y -= 20
        c.drawString(100, y, f"Detalle: {detalle}")
        y -= 20
        c.drawString(100, y, f"Stock: {stock}")
        y -= 20

    # Guarda y cierra el archivo PDF
    c.save()

    # Llama a la función para enviar el informe por correo
    informe_pdf_filename = f"Informe_Productos_{fecha_actual}.pdf"
    destinatario_email = "dhonwean@gmail.com"  # Reemplaza con la dirección de correo de la empresa
    enviar_informe_por_correo(informe_pdf_filename, destinatario_email)

    # Muestra un mensaje de éxito
    messagebox.showinfo("Informe Generado", f"El informe se ha generado y enviado a {destinatario_email}")
    #---------------------------------------------------------------

#-------------------------------------------------------
#CRERA FUNCION ENVIAR REPORTE POR CORREO

def enviar_informe_por_correo(informe_pdf_filename, destinatario_email):

    # Obtén la fecha actual
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    usuario_correo = "dhonwean@gmail.com"
    contrasena = "ykxubwitmoqnmrzv"

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(usuario_correo, contrasena)

    mensaje = MIMEMultipart()
    mensaje["From"] = usuario_correo
    mensaje["To"] = destinatario_email
    mensaje["Subject"] = (f"Informe de Inventario {fecha_actual}")

    mensaje.attach(MIMEText(f"Se hace envío del informe de inventario con fecha: {fecha_actual}."))

    with open(informe_pdf_filename, "rb") as pdf_file:
        adjunto = MIMEApplication(pdf_file.read(), _subtype="pdf")
        adjunto.add_header("Content-Disposition", f"attachment; filename={informe_pdf_filename}")
        mensaje.attach(adjunto)

    server.sendmail(usuario_correo, destinatario_email, mensaje.as_string())
    server.quit()
#--------------------------------------------------

#----------------------------------------------------
# Función de filtrado que se llama cuando se escribe en el Entry
def filtro_automatico(event):
    filtro = entry_filtro.get()
    
    listbox.delete(0, tk.END)
    conn = sqlite3.connect("Inventario.db")
    cursor = conn.cursor()

    # Utiliza una consulta SQL para filtrar los productos por nombre
    cursor.execute("SELECT nombre, detalle, stock, codigo FROM existencias WHERE nombre LIKE ?",
                   ('%' + filtro + '%',))  # Usamos % para buscar nombres que contengan el filtro

    existencias = cursor.fetchall()
    conn.close()

    for existencia in existencias:
        listbox.insert(tk.END, f"Nombre: {existencia[0]} | Detalle: {existencia[1]} | Stock: {existencia[2]} | Código: {existencia[3]}")
#---------------------------------------------------





#-------------------------------------------------
           



#----------------------------------------------------------
#CREAR LA VENTANA DE AGREGAR PRODUCTOS
def ventana_agregar_productos():

    global entry_nombre, entry_detalle, entry_stock, ventana_agregar

    ventana_agregar = tk.Toplevel(ventana)
    ventana_agregar.title("Agregar Producto [AISLA HOME]")
    ventana_agregar.geometry("300x300")
    ventana_agregar.grab_set()



    #AGREGAR LABELS, ENTRY AND BOTONES
    
    #---------------------------------------
    #NOMBRE
    lbl_nombre = tk.Label(ventana_agregar, text="Nombre:")
    lbl_nombre.pack()
    lbl_nombre.place(x=20, y=37)
    entry_nombre = tk.Entry(ventana_agregar)
    entry_nombre.pack()
    entry_nombre.place(x=20, y=60)
    #-----------------------------------------

    #------------------------------------------
    #DETALLE
    lbl_detalle = tk.Label(ventana_agregar, text="Detalle:")
    lbl_detalle.pack()
    lbl_detalle.place(x=20, y=90)
    entry_detalle = tk.Entry(ventana_agregar)
    entry_detalle.pack()
    entry_detalle.place(x=20, y=115)
    #--------------------------------------------

    #---------------------------------------------
    #STOCK
    lbl_stock = tk.Label(ventana_agregar, text="Stock:")
    lbl_stock.pack()
    lbl_stock.place(x=20, y=145)
    entry_stock = tk.Entry(ventana_agregar)
    entry_stock.pack()
    entry_stock.place(x=20, y=170)
    #---------------------------------------------

    #-----------------------------------------
    #BOTON AGREGAR
    btn_agregar = tk.Button(ventana_agregar, text="Agregar", command=agregar_producto)
    btn_agregar.pack()
    btn_agregar.place(x=200, y=250)
    #-------------------------------------------------
#-------------------------------------------------------------

#----------------------------------------------------------
#CREAR LA VENTANA DE EDITAR STOCK
def ventana_editar_producto():

    global entry_stock, entry_filtro_stock, listbox_stock, btn_filtrar_stock

    ventana_stock = tk.Toplevel(ventana)
    ventana_stock.title("Editar Stock [AISLA HOME]")
    ventana_stock.geometry("800x450")
    ventana_stock.grab_set()



    #AGREGAR LABELS, ENTRY AND BOTONES

   
    #-----------------------------------------------
    #FILTRO
    entry_filtro_stock = tk.Entry(ventana_stock, width=40)
    entry_filtro_stock.pack()
    entry_filtro_stock.place(x=300, y=40)

    #BOTON FILTRAR
    btn_filtrar_stock = tk.Button(ventana_stock,text="Filtrar", height=1, command=filtro_stock)
    btn_filtrar_stock.place(x=550,y=37)
    #------------------------------------------------

    #------------------------------------------------
    #STOCK
    lbl_stock = tk.Label(ventana_stock, text="Stock:")
    lbl_stock.pack()
    lbl_stock.place(x=20, y=70)
    entry_stock = tk.Entry(ventana_stock)
    entry_stock.pack()
    entry_stock.place(x=20, y=100)
    #-----------------------------------------------

    #-------------------------------------------
    #LISTA STOCK
    listbox_stock = tk.Listbox(ventana_stock, height= 20, width=100)
    listbox_stock.pack()
    listbox_stock.place(x=150,y=70)
    listbox_stock.bind("<<ListboxSelect>>", seleccionar_producto_stock)
    #-----------------------------------------------------

    #-------------------------------------------------------
    # Botón para agregar stock en la pantalla principal
    btn_agregar_stock = tk.Button(ventana_stock, text="Agregar Stock", command=lambda: editar_stock_producto_seleccionado("agregar"))
    btn_agregar_stock.place(x=670,y=400)
    #-------------------------------------------------------

    #------------------------------------------------------------
    # Botón para quitar stock en la pantalla principal
    btn_quitar_stock = tk.Button(ventana_stock, text="Quitar Stock", command=lambda: editar_stock_producto_seleccionado("quitar"))
    btn_quitar_stock.place(x=585, y=400)
    #-----------------------------------------------------------------------

    #----------------------------
    #LLAMAR FUNCIONES
    actualizar_lista_stock()
    #----------------------------

#----------------------------------------------------------






#----------------------------------------------------------






#--------------------------------------
#CREAR LA VENTANA PRINCIPAL

ventana = tk.Tk()
ventana.title("Inventario [AISLA HOME]")   
ventana.geometry("1000x600")




#----------------------------------------------
#FILTRO
entry_filtro = tk.Entry(ventana, width=40)
entry_filtro.pack()
entry_filtro.place(x=350, y=40)
entry_filtro.bind("<KeyRelease>", filtro_automatico)

#BOTON FILTRAR
btn_filtrar = tk.Button(ventana,text="Filtrar", height=1,command=filtro)
btn_filtrar.place(x=600.5,y=37)
#-------------------------------------------------

#------------------------------------------------
#LISTA#
listbox = tk.Listbox(ventana, height= 20, width=130)
listbox.pack()
listbox.place(x=100,y=70)
listbox.bind("<<ListboxSelect>>", seleccionar_producto)
#------------------------------------------------

#------------------------------------------------
#BOTON AGREGAR PRODUCTO
btn_agregar_producto = tk.Button(ventana, text="Agregar Producto", command=ventana_agregar_productos)
btn_agregar_producto.pack()
btn_agregar_producto.place(x=780,y=550)
#------------------------------------------------

#------------------------------------------------
#BOTON EDITAR
btn_editar = tk.Button(ventana,text="Editar Stock", command=ventana_editar_producto)
btn_editar.place(x=700,y=550)
#-----------------------------------------------

#-----------------------------------------------
#BOTON ELIMINAR PRODUCTO
btn_eliminar_producto = tk.Button(ventana,text="Eliminar Producto", command=eliminar_producto_seleccionado)
btn_eliminar_producto.place(x=587,y=550)
#----------------------------------------------

#---------------------------------------------
#MARCA DE LA DESARROLLADORA
lbl_marca = tk.Label(ventana,text="PulguitasDev.")
lbl_marca.pack()
lbl_marca.place(x=100,y=550)
#---------------------------------------------

#--------------------------------------
#BOTON DEL REPORTE
# Agrega un botón para generar el informe PDF
btn_generar_informe = tk.Button(ventana, text="Generar y Enviar Informe PDF por Correo", command=generar_informe_pdf)
btn_generar_informe.pack()
btn_generar_informe.place(x=700, y=500)

#---------------------------------------


#------------------------------------------
#LLAMAR FUNCIONES AL INICIAR SOFTWARE

crear_db()
actualizar_lista()
#-----------------------------------------

ventana.mainloop()