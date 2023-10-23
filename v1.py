import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
import sqlite3
import sys
import os

#----------------------------------------------
#GENERAR REPORTE
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime
#----------------------------------------------

#----------------------------------------------
#ENVIAR REPORTE POR CORREO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
#----------------------------------------------

#----------------------------------------------
#VARIABLES GLOBALES
codigo_seleccionado = None
codigo_seleccionado_stock = None
#----------------------------------------------

#----------------------------------------------
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
#----------------------------------------------

#----------------------------------------------
#LIMPIAR CAMPOS
def limpiar_campos_general():
    entry_nombre.delete(0,ctk.END)
    entry_detalle.delete(0,ctk.END)
    entry_stock.delete(0,ctk.END)
    
    
#----------------------------------------------

#----------------------------------------------
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
#----------------------------------------------

#----------------------------------------------
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
#----------------------------------------------

#----------------------------------------------
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

    # Validar stock
    if not stock.isdigit():
        messagebox.showerror("Error", "El stock debe ser un número.")
        return

    # Validar que stock no sea un carácter de texto
    if stock.isalpha():
        messagebox.showerror("Error", "El stock no debe ser un carácter de texto.")
        return    


   

#----------------------------------------------

#----------------------------------------------
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
                        entry_filtro_stock.delete(0, tk.END)  # Limpiar el campo de entrada de stock
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
#----------------------------------------------

#----------------------------------------------
#CREAR FUNCION ELIMINAR STOCK SELECCIONADO
def eliminar_producto_seleccionado():
    if codigo_seleccionado is not None:
        conn = sqlite3.connect("Inventario.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM existencias WHERE Codigo=?", (codigo_seleccionado,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Producto eliminado con éxito.")
        actualizar_lista()
#----------------------------------------------

#----------------------------------------------------------------
#FUNCION PARA MANEJAR LA SELECCION EN LA LISTA
def seleccionar_producto(event):
    global codigo_seleccionado, codigo_seleccionado_stock
    seleccion = listbox.curselection()
    if seleccion:
        codigo_seleccionado = int(listbox.get(seleccion[0]).split("Código: ")[1])
#--------------------------------------------------------------------

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

#--------------------------------------------------------------------
#FUNCION PARA MANEJAR LA SELECCION EN LA LISTA DEL STOCK
def seleccionar_producto_stock(event):
    global codigo_seleccionado_stock
    seleccion = listbox_stock.curselection()
    if seleccion:
        codigo_seleccionado_stock = int(listbox_stock.get(seleccion[0]).split("Código: ")[1])

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

#----------------------------------------------------
# Función de filtrado que se llama cuando se escribe en el Entry
def filtro_automatico_stock(event):
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
        listbox_stock.insert(tk.END, f"Nombre: {existencia[0]} | Detalle: {existencia[1]} | Stock: {existencia[2]} | Código: {existencia[3]}")
#---------------------------------------------------

#----------------------------------------------------------
#CREAR LA VENTANA DE AGREGAR PRODUCTOS
def ventana_agregar_productos():

    global entry_nombre, entry_detalle, entry_stock, ventana_agregar

    ventana_agregar = ctk.CTkToplevel(ventana)
    ventana_agregar.title("Agregar Producto [AISLA HOME]")
    ventana_agregar.geometry("180x300")
    ventana_agregar.grab_set()
    ventana_agregar.resizable(False, False)



    #AGREGAR LABELS, ENTRY AND BOTONES
    
    #---------------------------------------
    #NOMBRE
    lbl_nombre = ctk.CTkLabel(ventana_agregar, text="Nombre:")
    lbl_nombre.pack()
    lbl_nombre.place(x=20, y=37)
    entry_nombre = ctk.CTkEntry(ventana_agregar, border_color="#58B23E")
    entry_nombre.pack()
    entry_nombre.place(x=20, y=60)
    #-----------------------------------------

    #------------------------------------------
    #DETALLE
    lbl_detalle = ctk.CTkLabel(ventana_agregar, text="Detalle:")
    lbl_detalle.pack()
    lbl_detalle.place(x=20, y=90)
    entry_detalle = ctk.CTkEntry(ventana_agregar, border_color="#58B23E")
    entry_detalle.pack()
    entry_detalle.place(x=20, y=115)
    #--------------------------------------------

    #---------------------------------------------
    #STOCK
    lbl_stock = ctk.CTkLabel(ventana_agregar, text="Stock:")
    lbl_stock.pack()
    lbl_stock.place(x=20, y=145)
    entry_stock = ctk.CTkEntry(ventana_agregar, border_color="#58B23E")
    entry_stock.pack()
    entry_stock.place(x=20, y=170)
    #---------------------------------------------

    #-----------------------------------------
    #BOTON AGREGAR
    btn_agregar = ctk.CTkButton(ventana_agregar, text="Agregar", hover_color="#57D63E", fg_color="#58B23E", command=agregar_producto)
    btn_agregar.pack()
    btn_agregar.place(x=20, y=250)
    #-------------------------------------------------
#-------------------------------------------------------------

#----------------------------------------------------------
#CREAR LA VENTANA DE EDITAR STOCK
def ventana_editar_producto():

    global entry_stock, entry_filtro_stock, listbox_stock, btn_filtrar_stock

    ventana_stock = ctk.CTkToplevel(ventana)
    ventana_stock.title("Editar Stock [AISLA HOME]")
    ventana_stock.geometry("1000x600")
    ventana_stock.grab_set()
    ventana_stock.resizable(False, False)



    #----------------------------------------------
    #FILTRO
    entry_filtro_stock = ctk.CTkEntry(ventana_stock, width=400, border_color="#58B23E") #cambiar el tamaño
    entry_filtro_stock.pack()
    entry_filtro_stock.place(x=280, y=40)
    entry_filtro_stock.bind("<KeyRelease>", filtro_automatico_stock) #añadir filtro automatico

    #BOTON FILTRAR
    btn_filtrar_stock = ctk.CTkButton(ventana_stock, width=1, text="Buscar", hover_color="#57D63E", fg_color="#58B23E", command=filtro_stock)
    btn_filtrar_stock.pack()
    btn_filtrar_stock.place(x=690, y=39.9)
    #----------------------------------------------

    #----------------------------------------------
    #LISTA# 
    listbox_stock = tk.Listbox(ventana_stock)
    listbox_stock.config(bg="#343638", highlightcolor="#58B23E", highlightbackground="#58B23E",
                border=2, highlightthickness=5, fg="#FFFFFF")
    listbox_stock.config(height=20, width=90)
    listbox_stock.pack()
    listbox_stock.place(x=240, y=240)
    listbox_stock.config(font=("Arial", 30))
    listbox_stock.bind("<<ListboxSelect>>", seleccionar_producto_stock)
    #------------------------------------------------

    #------------------------------------------------
    #BOTON AGREGAR STOCK
    btn_agregar_stock = ctk.CTkButton(ventana_stock, text="Añadir Stock", width=1, hover_color="#57D63E", fg_color="#58B23E", command=lambda: editar_stock_producto_seleccionado("agregar"))
    btn_agregar_stock.pack()
    btn_agregar_stock.place(x=780, y=500)
#------------------------------------------------

    #BOTON QUITAR STOCK
    btn_agregar_stock = ctk.CTkButton(ventana_stock, text="Quitar Stock", width=1 ,hover_color="#57D63E", fg_color="#58B23E", command=lambda: editar_stock_producto_seleccionado("quitar"))
    btn_agregar_stock.pack()
    btn_agregar_stock.place(x=690, y=500)
    #------------------------------------------------

    #------------------------------------------------
    #ENTRY INGRESAR STOCK
    lbl_stock = ctk.CTkLabel(ventana_stock, text="Stock:")
    lbl_stock.pack()
    lbl_stock.place(x=490, y=500)
    entry_stock = ctk.CTkEntry(ventana_stock)
    entry_stock.pack()
    entry_stock.place(x=530, y=500)
    #------------------------------------------------
    #----------------------------
    #LLAMAR FUNCIONES
    actualizar_lista_stock()
    #----------------------------

#----------------------------------------------------------

#---------------------------------------------------
#FUNCION PARA EMPAQUETAR ICONOS
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)    
#---------------------------------------------------

#----------------------------------------------
#CREAR LA VENTANA PRINCIPAL
ventana = ctk.CTk()
ventana.title("Inventario [AISLA HOME]")
ventana.geometry("1000x600")
ventana.resizable(False, False)
ctk.set_appearance_mode("dark")

#path = resource_path("icon_logo.ico")
#ventana.iconbitmap(path)


#----------------------------------------------
#FILTRO
entry_filtro = ctk.CTkEntry(ventana, width=400, border_color="#58B23E") #cambiar el tamaño
entry_filtro.pack()
entry_filtro.place(x=280, y=40)
entry_filtro.bind("<KeyRelease>", filtro_automatico)

#BOTON FILTRAR
btn_filtrar = ctk.CTkButton(ventana, width=1, text="Buscar", hover_color="#57D63E", fg_color="#58B23E", command=filtro)
btn_filtrar.pack()
btn_filtrar.place(x=690, y=39.9)
#----------------------------------------------

#----------------------------------------------
#LISTA# 
listbox = tk.Listbox(ventana)
listbox.config(bg="#343638", highlightcolor="#58B23E", highlightbackground="#58B23E",
               border=2, highlightthickness=5, fg="#FFFFFF")
listbox.config(height=20, width=90)
listbox.pack()
listbox.place(x=240, y=240)
listbox.config(font=("Arial", 30))
listbox.bind("<<ListboxSelect>>", seleccionar_producto)
#------------------------------------------------

#------------------------------------------------
#BOTON AGREGAR PRODUCTO
btn_agregar_producto = ctk.CTkButton(ventana, text="Agregar Producto", width=1, hover_color="#57D63E", fg_color="#58B23E", command=ventana_agregar_productos)
btn_agregar_producto.pack()
btn_agregar_producto.place(x=780, y=500)
#------------------------------------------------

#------------------------------------------------
#BOTON EDITAR
btn_agregar_producto = ctk.CTkButton(ventana, text="Editar Stock", width=1 ,hover_color="#57D63E", fg_color="#58B23E", command=ventana_editar_producto)
btn_agregar_producto.pack()
btn_agregar_producto.place(x=690, y=500)
#------------------------------------------------

#------------------------------------------------
#BOTON ELIMINAR PRODUCTO
btn_agregar_producto = ctk.CTkButton(ventana, text="Eliminar Producto", width=1 ,hover_color="#57D63E", fg_color="#58B23E", command=eliminar_producto_seleccionado)
btn_agregar_producto.pack()
btn_agregar_producto.place(x=567, y=500)
#------------------------------------------------

#------------------------------------------------
#BOTON DEL REPORTE
btn_agregar_producto = ctk.CTkButton(ventana, text="Generar y Enviar Informe PDF por Correo", width=1 ,hover_color="#57D63E", fg_color="#58B23E", command=generar_informe_pdf)
btn_agregar_producto.pack()
#btn_agregar_producto.place(x=610, y=550)
btn_agregar_producto.place(x=314, y=500)
#------------------------------------------------

#------------------------------------------------
#MARCA DE LA DESARROLLADORA
lbl_marca = ctk.CTkLabel(ventana,text="PulguitasDev.")
lbl_marca.pack()
lbl_marca.place(x=10,y=570)
#------------------------------------------------

#------------------------------------------------
#LLAMAR FUNCIONES AL INICIAR SOFTWARE
crear_db()
actualizar_lista()
#------------------------------------------------

ventana.mainloop()
