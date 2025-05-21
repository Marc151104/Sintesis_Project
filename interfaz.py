from conexionDB import obtener_conexion
import pandas as pd  # type: ignore
import statsmodels.api as sm  # type: ignore
import tkinter as tk
from tkinter import ttk, messagebox
import folium  # type: ignore
import webbrowser
import heapq
import random
import math
from tkinter import messagebox

from itertools import combinations_with_replacement

import time
#--------------------------------------------------------


vehiculos = [
    {"nombre": "Furgoneta 1", "tipo": "Pequeña", "capacidad": 600, "costo_km": 0.52, "precio_compra": 500},
    {"nombre": "Furgoneta 2", "tipo": "Ligera",  "capacidad": 1000, "costo_km": 0.60, "precio_compra": 1000},
    {"nombre": "Furgoneta 3", "tipo": "Pesada",  "capacidad": 1500, "costo_km": 0.68, "precio_compra": 1500},
    {"nombre": "Camión 1",    "tipo": "Ligero",  "capacidad": 4000, "costo_km": 1.30, "precio_compra": 3000},
    {"nombre": "Camión 2",    "tipo": "Pesado",  "capacidad": 6000, "costo_km": 1.40, "precio_compra": 5000}
]


#VENTANA PRINCIPAL
root = tk.Tk()
root.title("Plataforma Logística")
root.geometry("700x500")
root.config(bg="#79a8d7")


#FRAME PRINCIPAL
frame_principal = tk.Frame(root, bg="#79a8d7")
frame_principal.pack(pady=50)


#--------------------------------------------------------


#MENÚ BOTONES
def mostrar_boton_principal():
    for widget in frame_principal.winfo_children():
        widget.destroy()


    boton_ver_tabla = tk.Button(frame_principal, text="Mostrar Pedidos", command=mostrar_pedidos)
    boton_ver_tabla.pack(pady=10)


    boton_calcular_rutas = tk.Button(frame_principal, text="Calcular Rutas", command=calcular_y_mostrar_rutas)
    boton_calcular_rutas.pack(pady=10)


    boton_ver_mapa = tk.Button(frame_principal, text="Mapa Puntos Entregas", command=mostrar_mapa_destinos)
    boton_ver_mapa.pack(pady=10)


    # Botón de cerrar
    boton_cerrar = tk.Button(frame_principal, text="Cerrar App", command=confirmar_cierre, bg="red", fg="white")
    boton_cerrar.pack(pady=10)


#--------------------------------------------------------


#CREDENCIALES
def mostrar_vista_credenciales():
    label_usuario = tk.Label(frame_principal, text="Usuario:", bg="#79a8d7", fg="black")
    label_usuario.grid(row=0, column=0, padx=10, pady=10)


    global entry_usuario
    entry_usuario = tk.Entry(frame_principal, bg="#79a8d7", fg="black")
    entry_usuario.grid(row=0, column=1, padx=10, pady=10)


    label_contrasena = tk.Label(frame_principal, text="Contraseña:", bg="#79a8d7", fg="black")
    label_contrasena.grid(row=1, column=0, padx=10, pady=10)


    global entry_contrasena
    entry_contrasena = tk.Entry(frame_principal, show="*", bg="#79a8d7", fg="black")
    entry_contrasena.grid(row=1, column=1, padx=10, pady=10)


    boton_registro = tk.Button(frame_principal, text="Registrar", command=registrar_usuario)
    boton_registro.grid(row=2, column=0, padx=10, pady=20)


    boton_cerrar = tk.Button(frame_principal, text="Cerrar App", command=confirmar_cierre, bg="red", fg="white")
    boton_cerrar.grid(row=2, column=1, padx=10, pady=20)


#CONFIRAMCIÓN DE CIERRE
def confirmar_cierre():
    respuesta = messagebox.askyesno("Confirmación", "¿Estás seguro de que deseas cerrar la aplicación?")
    if respuesta:
        root.destroy()


#REGISTRAR USUARIO
def registrar_usuario():
    usuario = entry_usuario.get()
    contrasena = entry_contrasena.get()


    if usuario == "admin" and contrasena == "123":
        messagebox.showinfo("Éxito", "Usuario registrado correctamente!")
   
        for widget in frame_principal.winfo_children():
            widget.destroy()
   
        mostrar_boton_principal()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos.")


#--------------------------------------------------------
# --- PEDIDOS ---


#OBTENER PEDIDOS
def tabla_pedidos():
    conn = obtener_conexion()
    if conn is None:
        return None


    query = """
    SELECT fecha_pedido, id_destino, COUNT(*) AS total_pedidos,
    GROUP_CONCAT(id_pedido ORDER BY id_pedido) AS ids_pedidos FROM  plataforma_logistica.pedidos
    GROUP BY fecha_pedido, id_destino ORDER BY fecha_pedido, id_destino;
    """


    tabla_pedidos = pd.read_sql(query, conn)
    conn.close()
    return tabla_pedidos


#MOSTRAR PEDIDOS
def mostrar_pedidos():
    for widget in frame_principal.winfo_children():
        widget.destroy()


    frame_tabla = tk.Frame(frame_principal, bg="#79a8d7", padx=20, pady=20)
    frame_tabla.pack(expand=True, fill="both", padx=10, pady=10)


    boton_volver = tk.Button(frame_tabla, text="Volver", command=mostrar_boton_principal, bg="#d9e6f2", fg="black")
    boton_volver.pack(pady=10, anchor="ne")


    df = tabla_pedidos()
    if df is not None:
        tabla = ttk.Treeview(frame_tabla, columns=("Fecha", "Destino", "Total Pedidos", "IDs Pedidos"), show="headings")
        tabla.heading("Fecha", text="Fecha Pedido")
        tabla.heading("Destino", text="ID Destino")
        tabla.heading("Total Pedidos", text="Total Pedidos")
        tabla.heading("IDs Pedidos", text="IDs de Pedidos")


        for i, row in df.iterrows():
            tabla.insert("", "end", values=(row["fecha_pedido"], row["id_destino"], row["total_pedidos"], row["ids_pedidos"]))
       
        tabla.pack(expand=True, fill="both", pady=10)


        scrollbar_x = tk.Scrollbar(frame_tabla, orient="horizontal", command=tabla.xview)
        tabla.configure(xscrollcommand=scrollbar_x.set)
        scrollbar_x.pack(fill="x", pady=5)


    else:
        messagebox.showerror("Error", "No se pudo cargar la tabla de pedidos.")


#--------------------------------------------------------


# --- MOSTRAR MAPA DESTINOS ---
def mostrar_mapa_destinos():
    for widget in frame_principal.winfo_children():
        widget.destroy()


    boton_volver = tk.Button(frame_principal, text="Volver", command=mostrar_boton_principal)
    boton_volver.pack(pady=10, anchor="ne")


    conn = obtener_conexion()
    if conn is None:
        print("Error: No se pudo conectar a la base de datos.")
        return


    query = """SELECT nombre, latitud, longitud FROM plataforma_logistica.ciudades"""
    try:
        destinos = pd.read_sql(query, conn)
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        conn.close()
        return


    conn.close()


    mapa = folium.Map(location=[40.4637, -3.7492], zoom_start=6)


    for _, row in destinos.iterrows():
        try:
            latitud = row['latitud']
            longitud = row['longitud']
            nombre = row['nombre']
            color = "green" if nombre.lower() == "mataro" else "blue"


            folium.Marker([latitud, longitud], popup=nombre, icon=folium.Icon(color=color)).add_to(mapa)
        except KeyError:
            pass


    mapa.save("mapa_destinos.html")
    webbrowser.open("mapa_destinos.html")


#--------------------------------------------------------


# --- MOSTRAR MAPA RUTAS ---


#GRAFO DISTÁNCIAS
def grafo_distancias():
    conn = obtener_conexion()
    grafo = {}
    try:
        query = "SELECT ciudad1, ciudad2, distancia FROM plataforma_logistica.distancias;"
        cursor = conn.cursor()
        cursor.execute(query)
        resultados = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]
        distancias_df = pd.DataFrame(resultados, columns=columnas)
   
        for _, fila in distancias_df.iterrows():
            ciudad1, ciudad2, distancia = fila['ciudad1'], fila['ciudad2'], fila['distancia']
            if ciudad1 not in grafo:
                grafo[ciudad1] = []
            if ciudad2 not in grafo:
                grafo[ciudad2] = []
            grafo[ciudad1].append((ciudad2, distancia))
            grafo[ciudad2].append((ciudad1, distancia))
    finally:
        conn.close()
    return grafo


#ALGORITMO DIJKSTRA
def dijkstra(grafo, inicio, destino):
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[inicio] = 0
    predecesores = {nodo: None for nodo in grafo}
    cola_prioridad = [(0, inicio)]


    while cola_prioridad:
        distancia_actual, nodo_actual = heapq.heappop(cola_prioridad)


        if nodo_actual == destino:
            break


        if distancia_actual > distancias[nodo_actual]:
            continue


        for vecino, peso in grafo[nodo_actual]:
            distancia_nueva = distancia_actual + peso
            if distancia_nueva < distancias[vecino]:
                distancias[vecino] = distancia_nueva
                predecesores[vecino] = nodo_actual
                heapq.heappush(cola_prioridad, (distancia_nueva, vecino))


    ruta = []
    nodo = destino
    while nodo is not None:
        ruta.insert(0, nodo)
        nodo = predecesores[nodo]


    return ruta, distancias[destino]




#CALCULAR RUTAS ÓPTIMAS
def calcular_ruta_para_pedidos(pedidos):
    grafo = grafo_distancias()
    rutas = []


    #Generar rutas para todos los pedidos
    for pedido in pedidos:
        inicio = 2  #Ciudad base Mataró ID=2
        destino = pedido['destino']
        ruta_optima, distancia_total = dijkstra(grafo, inicio, destino)


        rutas.append({
            'pedido_id': pedido['id_pedido'],
            'cliente': pedido['cliente'],
            'destino': destino,
            'ruta': ruta_optima,
            'distancia_total': distancia_total,
            'cantidad': pedido['cantidad']
        })


    #Ordenar las rutas por distancia en orden descendente
    rutas.sort(key=lambda x: x['distancia_total'], reverse=True)


    return rutas




#CLACULAR RUTAS ORDENADAS
def calcular_rutas_ordenadas(pedidos):
    rutas = calcular_ruta_para_pedidos(pedidos)
    rutas_ordenadas = []
    ciudades_visitadas = set()


    for ruta in rutas:
        #Ignorar rutas cuyo destino ya fue visitado
        if ruta['destino'] in ciudades_visitadas:
            continue


        #Marcar las ciudades intermedias como visitadas
        for ciudad in ruta['ruta']:
            ciudades_visitadas.add(ciudad)


        rutas_ordenadas.append(ruta)


    return rutas_ordenadas




#OBTENER CIUDADES
def obtener_ciudades():
    conn = obtener_conexion()
    ciudades = {}
    try:
        query = "SELECT id_ciudades, nombre, latitud, longitud FROM plataforma_logistica.ciudades;"
        ciudades_df = pd.read_sql(query, conn)
        for _, fila in ciudades_df.iterrows():
            ciudades[fila['id_ciudades']] = {
                'nombre': fila['nombre'],
                'coords': [fila['latitud'], fila['longitud']]
            }
    finally:
        conn.close()
    return ciudades




#COLOR ALEATORIO
def generar_color_random():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))




#VISUALIZAR MAPA DE RUTAS
def visualizar_rutas(rutas):
    ciudades = obtener_ciudades()
    mapa = folium.Map(location=ciudades[2]['coords'], zoom_start=6)


    rutas_ordenadas = sorted(rutas, key=lambda r: r['distancia_total'], reverse=True)


    #Crear una capa para cada ruta
    capas_rutas = []
    for idx, ruta in enumerate(rutas_ordenadas):
        capa = folium.FeatureGroup(name=f"Ruta {idx + 1}: {ruta['distancia_total']} km")
        color_ruta = generar_color_random()
        for j in range(len(ruta['ruta']) - 1):
            origen = ciudades[ruta['ruta'][j]]['coords']
            destino = ciudades[ruta['ruta'][j + 1]]['coords']
            folium.PolyLine([origen, destino], color=color_ruta, weight=3, opacity=0.6).add_to(capa)
        capas_rutas.append(capa)
        capa.add_to(mapa)


    #Añadir marcadores de ciudades
    for ciudad_id, ciudad in ciudades.items():
        folium.Marker(
            location=ciudad['coords'],
            popup=folium.Popup(f"<b>{ciudad['nombre']}</b>", max_width=300),
        ).add_to(mapa)


    folium.LayerControl(collapsed=False).add_to(mapa)
    mapa.save("rutas_pedidos_colores.html")


    #Insertar script para checkbox "All"
    with open("rutas_pedidos_colores.html", "r") as file:
        contenido = file.read()


    script_all = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            var checkboxes = document.querySelectorAll('input[type=\"checkbox\"]');
            var allCheckbox = document.createElement('input');
            allCheckbox.type = 'checkbox';
            allCheckbox.id = 'all-routes';
            var label = document.createElement('label');
            label.htmlFor = 'all-routes';
            label.textContent = ' All';
            var controls = document.querySelector('.leaflet-control-layers-list');
            controls.insertBefore(allCheckbox, controls.firstChild);
            controls.insertBefore(label, allCheckbox.nextSibling);
            allCheckbox.addEventListener('change', function() {
                checkboxes.forEach(function(checkbox) {
                    checkbox.checked = allCheckbox.checked;
                    checkbox.dispatchEvent(new Event('change'));
                });
            });
        });
    </script>
    """
    contenido = contenido.replace("</body>", script_all + "</body>")


    with open("rutas_pedidos_colores.html", "w") as file:
        file.write(contenido)




#OBTENER FECHA MÁX/MIN CADUCIDAD PEDIDIDOS
def fecha_caducidad():
    conn = obtener_conexion()
    if conn is None:
        return None


    query = """
    SELECT p.fecha_pedido, p.id_destino, COUNT(*) AS total_pedidos,
    GROUP_CONCAT(p.id_pedido ORDER BY p.id_pedido) AS ids_pedidos,
    MAX(prod.caducidad_desde_fabricacion) AS fecha_fabricacion_max,
    MIN(prod.caducidad_desde_fabricacion) AS fecha_fabricacion_min,
    SUM(p.cantidad) AS total_productos, SUM(prod.precio_venta) as total_precio_venta
    FROM plataforma_logistica.pedidos p
    JOIN plataforma_logistica.producto prod ON p.id_producto = prod.id_producto
    GROUP BY p.fecha_pedido,
    p.id_destino ORDER BY p.fecha_pedido, p.id_destino;
    """


    fecha_caducidad = pd.read_sql(query, conn)
    conn.close()
    return fecha_caducidad


#OBTENER DATOS DE PEDIDOS
def obtener_pedidos():
    conn = obtener_conexion()
    try:
        query = """
        SELECT p.id_pedido, p.fecha_pedido, p.cantidad,
            c.nombre AS cliente, d.id_destino AS destino,
            prod.nombre AS producto, prod.precio_venta
        FROM plataforma_logistica.pedidos p
        JOIN plataforma_logistica.Clientes c ON p.id_cliente = c.id_cliente
        JOIN plataforma_logistica.Destinos d ON p.id_destino = d.id_destino
        JOIN plataforma_logistica.Producto prod ON p.id_producto = prod.id_producto
        """
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        pedidos = cursor.fetchall()
        return pedidos
    finally:
        conn.close()


    camiones_por_destino = {}


    for pedido in pedidos:
        destino = pedido['destino']
        cantidad = pedido['cantidad']


        if destino not in camiones_por_destino:
            camiones_por_destino[destino] = 0
        camiones_por_destino[destino] += cantidad


    for destino, total in camiones_por_destino.items():
            raise ValueError("La capacidad del camión debe ser un valor positivo y mayor que cero.")


    print('camiones_por_destino:', camiones_por_destino)
    return camiones_por_destino


    try:
            raise ValueError("La capacidad del camión debe ser un número positivo.")
    except ValueError as e:
        messagebox.showerror("Error", f"Entrada inválida en Capacidad Camión: {e}")
        return


    pedidos = obtener_pedidos()
    if not pedidos:
        messagebox.showerror("Error", "No se encontraron pedidos para calcular.")
        return


    for destino, camiones in camiones_por_destino.items():
        print(f"Destino (Ruta): {destino}, Camiones necesarios: {camiones}")


    messagebox.showinfo("Camiones Calculados", "Se ha calculado el número de camiones necesarios. Revise la consola para detalles.")


#------------------------------------------------------------------------------------------------------------------------------------


#IMPRIMIR LISTADO DE RUTAS
def imprimir_rutas(rutas):
    ciudades = obtener_ciudades()


    rutas_unicas = set()
    for ruta in rutas:
        nombres_ruta = tuple(ciudades[ciudad_id]['nombre'] for ciudad_id in ruta['ruta'])
        distancia_total = ruta['distancia_total']
        rutas_unicas.add((nombres_ruta, distancia_total))


    for i, (nombres_ruta, distancia_total) in enumerate(rutas_unicas, start=1):
        ruta_str = f"Ruta n°{i}: " + " -> ".join(nombres_ruta) + f" | Kilómetros totales: {distancia_total} km"
        print(ruta_str)



def asignar_mejor_flotilla(carga_total, distancia_km):
    mejor_opcion = None
    menor_num_vehiculos = float('inf')
    menor_costo = float('inf')

    flota = sorted(vehiculos, key=lambda v: -v['capacidad'])  # empezar con los más grandes

    for n in range(1, 11):  # puedes subir el máximo si quieres más opciones
        for combinacion in combinations_with_replacement(flota, n):
            carga_total_comb = sum(v['capacidad'] for v in combinacion)
            if carga_total_comb < carga_total:
                continue  # no alcanza la carga total, descartar

            costo_total = sum(distancia_km * v['costo_km'] for v in combinacion)

            if (n < menor_num_vehiculos) or (n == menor_num_vehiculos and costo_total < menor_costo):
                conteo = {}
                for v in combinacion:
                    nombre = v['nombre']
                    conteo[nombre] = conteo.get(nombre, 0) + 1

                mejor_opcion = []
                for nombre, cantidad in conteo.items():
                    v = next(v for v in vehiculos if v['nombre'] == nombre)
                    mejor_opcion.append({
                        'vehiculo': nombre,
                        'capacidad': v['capacidad'],
                        'cantidad': cantidad,
                        'costo_total': cantidad * distancia_km * v['costo_km'],
                        'precio_compra': v['precio_compra']  # ✅ se incluye el precio de compra aquí
                    })

                menor_num_vehiculos = n
                menor_costo = costo_total

    return mejor_opcion



def calcular_tiempo_y_camiones_rutas(rutas):
    try:
        velocidad_media = float(entry_velocidad_media.get())  # Velocidad en km/h
        if velocidad_media <= 0:
            raise ValueError("La velocidad_media debe ser un número positivo.")
    except ValueError as e:
        messagebox.showerror("Error", f"Entrada inválida en Velocidad Media: {e}")
        return


    horas_conduccion_diaria = 8
    ciudades = obtener_ciudades()
    pedidos = obtener_pedidos()  # Obtén los pedidos para calcular los camiones necesarios por ciudad
    resultados_rutas = []
   
    # Conjunto global de ciudades procesadas (esto se acumula durante el cálculo de todas las rutas)
    ciudades_procesadas_globales = set()  


    for i, ruta in enumerate(rutas, start=1):
        distancia_total = ruta['distancia_total']


        # Calculamos el tiempo total de la ruta
        tiempo_total_horas = distancia_total / velocidad_media
        dias_completos, horas_restantes = divmod(tiempo_total_horas, horas_conduccion_diaria)
        dias = int(dias_completos)
        horas = round(horas_restantes)

        # Conjunto para almacenar las ciudades procesadas solo en esta ruta
        ciudades_procesadas = set()  
        total_carga = 0  # Contador de la cantidad total de productos

        for ciudad_id in ruta['ruta']:  # Itera sobre las ciudades de la ruta
            if ciudad_id not in ciudades_procesadas_globales:  # Si la ciudad no ha sido procesada en ninguna ruta previa
                # Filtra los pedidos que corresponden a esa ciudad
                pedidos_ciudad = [pedido for pedido in pedidos if pedido['destino'] == ciudad_id]
                for pedido in pedidos_ciudad:
                    total_carga += pedido['cantidad']


                # Marca la ciudad como procesada para esta ruta (para no contarla nuevamente en esta ruta)
                ciudades_procesadas.add(ciudad_id)


        # Agregar las ciudades procesadas de esta ruta al conjunto global
        ciudades_procesadas_globales.update(ciudades_procesadas)


        asignacion = asignar_mejor_flotilla(total_carga, distancia_total)
        for veh in asignacion:
            print(f"  -> {veh['cantidad']} x {veh['vehiculo']} (capacidad: {veh['capacidad']} kg, costo: {veh['costo_total']:.2f} €)")
        camiones_necesarios = sum(v['cantidad'] for v in asignacion)

        # Mostrar la cantidad total de productos para cada ruta
        print(f"Ruta n°{i}: Cantidad total de productos: {total_carga} unidades.")


        # Construcción de la cadena de nombres de las ciudades en la ruta
        nombres_ciudades = " -> ".join(ciudades[ciudad_id]['nombre'] for ciudad_id in ruta['ruta'])
        tiempo_str = f"{dias} días y {horas:.2f} horas"


        camiones_necesarios = sum(v['cantidad'] for v in asignacion)


        resultados_rutas.append({
            'ruta_id': i,
            'nombres_ciudades': nombres_ciudades,
            'distancia_total': distancia_total,
            'dias': dias,
            'horas': horas,
            'tiempo_estimado': dias + (horas / horas_conduccion_diaria),
            'camiones_necesarios': camiones_necesarios,
            'vehiculos_usados': asignacion,
            'destino': ruta.get('destino')  # <--- esta línea añade el destino
        })


        # Mostrar los resultados finales de la ruta en la terminal
        print(f"Ruta n°{i}: {nombres_ciudades} | Distancia total: {distancia_total} km | "
              f"Tiempo estimado: {tiempo_str} | Camiones necesarios: {camiones_necesarios}")

    return resultados_rutas

def calcular_costos_rutas(resultados_tiempos_y_camiones):
    HORAS_JORNADA = 8
    SALARIO_POR_DIA = 70
    pedidos = obtener_pedidos()
    costos_por_ruta = []

    for resultados in resultados_tiempos_y_camiones:
        ruta_id = resultados['ruta_id']
        distancia_total = resultados['distancia_total']
        camiones_usados = resultados['vehiculos_usados']
        camiones_necesarios = resultados['camiones_necesarios']
        tiempo_estimado = resultados['tiempo_estimado']
        destino = resultados['destino']

        # Costo de camiones
        costo_camiones = sum(v['cantidad'] * v['precio_compra'] for v in camiones_usados)

        

        # Costo por kilómetro
        costo_km = sum(v['costo_total'] for v in camiones_usados)
        costo_por_km = costo_km / distancia_total if distancia_total else 0

        # Salario camioneros
        tiempo_horas = tiempo_estimado * HORAS_JORNADA
        dias = int(tiempo_horas // HORAS_JORNADA)
        if tiempo_horas % HORAS_JORNADA != 0:
            dias += 1
        salario_total = camiones_necesarios * dias * SALARIO_POR_DIA

        # Costo total
        costo_total = costo_camiones + salario_total * costo_por_km

        # Ganancias
        ganancias = sum(p['precio_venta'] * p['cantidad'] for p in pedidos if p['destino'] == destino) - costo_total

        # Añadir al listado final
        costos_por_ruta.append({
            'ruta_id': ruta_id,
            'distancia_total': distancia_total,
            'costo_camiones': costo_camiones,
            'costo_por_km': costo_por_km,
            'costo_total': costo_total,
            'ganancias': ganancias
        })

    return costos_por_ruta



#CALCULAR RUTAS
def calcular_rutas():
    pedidos = obtener_pedidos()
    rutas_ordenadas = calcular_rutas_ordenadas(pedidos)

    if rutas_ordenadas:
        # Asegurar estructura esperada por calcular_tiempo_y_camiones_rutas
        rutas_con_formato = []
        for ruta in rutas_ordenadas:
            rutas_con_formato.append({
                'ruta_id': ruta['pedido_id'],
                'ruta': ruta['ruta'],
                'distancia_total': ruta['distancia_total'],
                'destino': ruta['destino']
            })
                
        # Luego llama con ese formato
        resultados_tiempos_y_camiones = calcular_tiempo_y_camiones_rutas(rutas_con_formato)
      
        costos_por_ruta = calcular_costos_rutas(resultados_tiempos_y_camiones)
        
        for widget in frame_principal.winfo_children():
            widget.destroy()

        boton_mostrar_mapa = tk.Button(frame_principal, text="Mostrar Mapa", command=lambda: mostrar_mapa_rutas_ordenadas(rutas_ordenadas), bg="#d9e6f2", fg="black")
        boton_mostrar_mapa.grid(row=3, column=0, padx=10, pady=20)
       
        boton_mostrar_costos = tk.Button(frame_principal, text="Mostrar Costos", command=lambda: mostrar_costos(costos_por_ruta), bg="#d9e6f2", fg="black")
        boton_mostrar_costos.grid(row=3, column=2, padx=10, pady=20)

        boton_volver = tk.Button(frame_principal, text="Volver", command=calcular_y_mostrar_rutas, bg="#d9e6f2", fg="black")
        boton_volver.grid(row=3, column=3, padx=10, pady=20, sticky="w")
       
    else:
        messagebox.showerror("Error", "No se encontraron rutas para mostrar.")

# MOSTRAR MAPA
def mostrar_mapa_rutas_ordenadas(rutas_ordenadas):
    visualizar_rutas(rutas_ordenadas)
    webbrowser.open("rutas_pedidos_colores.html")


# MOSTRAR DATOS DE LAS RUTAS EN UNA TABLA
def mostrar_datos_rutas(rutas_ordenadas):
    for widget in frame_principal.winfo_children():
        widget.destroy()

    frame_tabla = tk.Frame(frame_principal, bg="#79a8d7", padx=20, pady=20)
    frame_tabla.pack(expand=True, fill="both", padx=10, pady=10)

    boton_volver = tk.Button(frame_tabla, text="Volver", command=calcular_y_mostrar_rutas, bg="#d9e6f2", fg="black")
    boton_volver.pack(pady=10, anchor="ne")

    if rutas_ordenadas:
        tabla = ttk.Treeview(
            frame_tabla,
            columns=("Ruta", "Distancia Total (km)", "Tiempo Estimado (días y horas)", "Camiones Necesarios"),
            show="headings"
        )
       
        tabla.heading("Ruta", text="Ruta")
        tabla.heading("Distancia Total (km)", text="Distancia Total (km)")
        tabla.heading("Tiempo Estimado (días y horas)", text="Tiempo Estimado (días y horas)")
        tabla.heading("Camiones Necesarios", text="Camiones Necesarios")

        tabla.column("Ruta", width=200, anchor="center")
        tabla.column("Distancia Total (km)", width=150, anchor="center")
        tabla.column("Tiempo Estimado (días y horas)", width=200, anchor="center")
        tabla.column("Camiones Necesarios", width=150, anchor="center")

        for i, ruta in enumerate(rutas_ordenadas, start=1):
            try:
                tabla.insert(
                    "", "end",
                    values=(
                        f"Ruta n°{ruta['ruta_id']}",
                        f"{ruta['distancia_total']} km",
                        f"{ruta['dias']} días y {ruta['horas']:.2f} horas",
                        f"{ruta['camiones_necesarios']}"
                    )
                )
            except KeyError as e:
                messagebox.showerror("Error", f"Datos incompletos en la ruta: {e}")
                return

        tabla.pack(expand=True, fill="both", pady=10)
        scrollbar_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
        scrollbar_y.pack(side="right", fill="y")
        tabla.configure(yscrollcommand=scrollbar_y.set)

    else:
        messagebox.showerror("Error", "No hay rutas disponibles para mostrar.")


# MOSTRAR COSTOS POR RUTA EN UNA TABLA
def mostrar_costos(costos_por_ruta):
    for widget in frame_principal.winfo_children():
        widget.destroy()

    frame_tabla = tk.Frame(frame_principal, bg="#79a8d7", padx=20, pady=20)
    frame_tabla.pack(expand=True, fill="both", padx=10, pady=10)

    boton_volver = tk.Button(frame_tabla, text="Volver", command=calcular_y_mostrar_rutas, bg="#d9e6f2", fg="black")
    boton_volver.pack(pady=10, anchor="ne")

    columnas = [
        "Ruta ID",
        "Distancia Total (km)",
        "Precio Camiones por Ruta",
        "€/km",
        "Costo Total",
        "Ganancias por Ruta"
    ]

    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, anchor="center")

    total_distancia = 0
    total_camiones_precio = 0.0
    total_costo = 0.0
    total_ganancias = 0.0

    for costo in costos_por_ruta:
        tabla.insert("", tk.END, values=(
            costo['ruta_id'],
            f"{costo['distancia_total']} km",
            f"{costo['costo_camiones']:.2f} €",
            f"{costo['costo_por_km']:.2f} €",
            f"{costo['costo_total']:.2f} €",
            f"{costo['ganancias']:.2f} €"
        ))

        total_distancia += costo['distancia_total']
        total_camiones_precio += costo['costo_camiones']
        total_costo += costo['costo_total']
        total_ganancias += float(costo['ganancias'])

    # Fila de totales
    tabla.insert("", "end", values=(
        "Total",
        f"{total_distancia} km",
        f"{total_camiones_precio:.2f} €",
        "",  # €/km no aplica
        f"{total_costo:.2f} €",
        f"{total_ganancias:.2f} €"
    ))

    tabla.pack(expand=True, fill="both", pady=10)

    scrollbar_x = tk.Scrollbar(frame_tabla, orient="horizontal", command=tabla.xview)
    tabla.configure(xscrollcommand=scrollbar_x.set)
    scrollbar_x.pack(fill="x", pady=5)


#MOSTRAR RUTAS
def calcular_y_mostrar_rutas():
    for widget in frame_principal.winfo_children():
        widget.destroy()

    label_velocidad_media = tk.Label(frame_principal, text="Velocidad Media:", bg="#79a8d7", fg="black")
    label_velocidad_media.grid(row=2, column=0, padx=10, pady=10)

    global entry_velocidad_media
    entry_velocidad_media = tk.Entry(frame_principal, bg="#79a8d7", fg="black")
    entry_velocidad_media.grid(row=2, column=1, padx=10, pady=10)

    boton_volver = tk.Button(frame_principal, text="Volver", command=mostrar_boton_principal, bg="#d9e6f2", fg="black")
    boton_volver.grid(row=3, column=0, padx=10, pady=20, sticky="w")

    boton_calcular_rutas = tk.Button(frame_principal, text="Calcular Rutas", command=calcular_rutas, bg="#d9e6f2", fg="black")
    boton_calcular_rutas.grid(row=3, column=1, padx=10, pady=20, sticky="e")

#--------------------------------------------------------------------------

#EMPEZAR PROGRAMA
#Llama a las credenciales
mostrar_vista_credenciales()
#Inicia el programa
root.mainloop()