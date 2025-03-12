from flask import Flask, render_template, request, jsonify, make_response
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('datos.db')
    conn.row_factory = sqlite3.Row
    return conn

# Configuración de las tablas y sus campos
CRUD_CONFIG = {
    'Gestión de trabajadores': {
        'titulo': 'Gestión de Trabajadores',
        'tabla': 'Trabajadores',
        'icon': 'fas fa-users'
    },
    'Gestión de Clientes': {
        'titulo': 'Gestión de Clientes',
        'tabla': 'Clientes',
        'icon': 'fas fa-user-tie'
    },
    'Gestión de Labores': {
        'titulo': 'Gestión de Labores',
        'tabla': 'Labores',
        'icon': 'fas fa-tasks'
    },
    'Gestión de equipos': {
        'titulo': 'Gestión de Equipos',
        'tabla': 'Equipos',
        'icon': 'fas fa-tools'
    }
}

@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/crud', methods=['POST'])
def crud():
    boton = request.form.get('submit')
    if boton in CRUD_CONFIG:
        return render_template('CRUD.html', config=CRUD_CONFIG[boton])
    elif boton == 'Administración de sueldos':
        return render_template('sueldos.html')
    return render_template('menu.html')

@app.route('/obtener_registros')
def obtener_registros():
    tabla = request.args.get('tabla', 'Trabajadores')
    conn = get_db_connection()
    
    if tabla == 'Labores':
        registros = conn.execute('SELECT Id, Nombre, Jornada, Valor FROM Labores WHERE Estado != "1" OR Estado IS NULL').fetchall()
        conn.close()
        return jsonify([{
            'id': registro['Id'], 
            'nombre': registro['Nombre'],
            'jornada': registro['Jornada'],
            'valor': registro['Valor']
        } for registro in registros])
    else:
        registros = conn.execute(f'SELECT Id, Nombre FROM {tabla} WHERE Estado != "1" OR Estado IS NULL').fetchall()
        conn.close()
        return jsonify([{'id': registro['Id'], 'nombre': registro['Nombre']} for registro in registros])

@app.route('/crear_registro', methods=['POST'])
def crear_registro():
    try:
        data = request.get_json()
        nombre = data.get('nombre')
        tabla = data.get('tabla')
        
        conn = get_db_connection()

        if tabla == 'Labores':
            # Para Labores necesitamos jornada y valor
            jornada = data.get('jornada')
            valor = data.get('valor', 0)
            
            if not jornada:
                return jsonify({
                    'success': False,
                    'error': 'La jornada es requerida para las labores'
                })
            
            # Verificar si existe la combinación nombre-jornada
            existente = conn.execute(
                'SELECT Id FROM Labores WHERE Nombre = ? AND Jornada = ? AND (Estado != "1" OR Estado IS NULL)',
                (nombre, jornada)
            ).fetchone()
            
            if existente:
                conn.close()
                return jsonify({
                    'success': False,
                    'error': f'Ya existe la labor {nombre} para la jornada {jornada}'
                })
            
            # Crear la labor con su jornada y valor
            conn.execute(
                'INSERT INTO Labores (Nombre, Jornada, Valor, Estado) VALUES (?, ?, ?, "0")',
                (nombre, jornada, valor)
            )
        else:
            # Para las demás tablas, verificar solo el nombre
            existente = conn.execute(
                f'SELECT Id FROM {tabla} WHERE Nombre = ? AND (Estado != "1" OR Estado IS NULL)',
                (nombre,)
            ).fetchone()
            
            if existente:
                conn.close()
                return jsonify({
                    'success': False,
                    'error': 'Ya existe un registro con ese nombre'
                })
            
            # Crear el registro normal
            conn.execute(f'INSERT INTO {tabla} (Nombre, Estado) VALUES (?, "0")', (nombre,))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'error': 'Error al crear el registro'
        })

@app.route('/actualizar_registro', methods=['POST'])
def actualizar_registro():
    try:
        data = request.get_json()
        id = data.get('id')
        nombre = data.get('nombre')
        tabla = data.get('tabla')
        
        conn = get_db_connection()

        if tabla == 'Labores':
            # Para Labores necesitamos jornada y valor
            jornada = data.get('jornada')
            valor = data.get('valor', 0)
            
            if not jornada:
                return jsonify({
                    'success': False,
                    'error': 'La jornada es requerida para las labores'
                })
            
            # Verificar si existe otra labor con el mismo nombre y jornada
            existente = conn.execute(
                'SELECT Id FROM Labores WHERE Nombre = ? AND Jornada = ? AND Id != ? AND (Estado != "1" OR Estado IS NULL)',
                (nombre, jornada, id)
            ).fetchone()
            
            if existente:
                conn.close()
                return jsonify({
                    'success': False,
                    'error': f'Ya existe la labor {nombre} para la jornada {jornada}'
                })
            
            # Actualizar la labor
            conn.execute(
                'UPDATE Labores SET Nombre = ?, Jornada = ?, Valor = ? WHERE Id = ?',
                (nombre, jornada, valor, id)
            )
        else:
            # Para las demás tablas, verificar solo el nombre
            existente = conn.execute(
                f'SELECT Id FROM {tabla} WHERE Nombre = ? AND Id != ? AND (Estado != "1" OR Estado IS NULL)',
                (nombre, id)
            ).fetchone()
            
            if existente:
                conn.close()
                return jsonify({
                    'success': False,
                    'error': 'Ya existe otro registro con ese nombre'
                })
            
            # Actualizar el registro normal
            conn.execute(f'UPDATE {tabla} SET Nombre = ? WHERE Id = ?', (nombre, id))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'error': 'Error al actualizar el registro'
        })

@app.route('/eliminar_registro', methods=['POST'])
def eliminar_registro():
    try:
        data = request.get_json()
        id = data.get('id')
        tabla = data.get('tabla')
        
        conn = get_db_connection()
        conn.execute(f'UPDATE {tabla} SET Estado = "1" WHERE Id = ?', (id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return jsonify({'success': False})

@app.route('/actualizar_sueldo', methods=['POST'])
def actualizar_sueldo():
    try:
        data = request.get_json()
        labor_id = data.get('labor_id')
        valor = data.get('valor')
        jornada = data.get('jornada')
        
        conn = get_db_connection()
        conn.execute('UPDATE Labores SET Valor = ? WHERE Id = ? AND Jornada = ?', 
                    (valor, labor_id, jornada))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return jsonify({'success': False})

@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

@app.route('/obtener_opciones')
def obtener_opciones():
    tipo = request.args.get('tipo')
    conn = get_db_connection()
    
    if tipo == 'trabajadores':
        registros = conn.execute('SELECT Id, Nombre FROM Trabajadores WHERE Estado != "1" OR Estado IS NULL').fetchall()
    elif tipo == 'clientes':
        registros = conn.execute('SELECT Id, Nombre FROM Clientes WHERE Estado != "1" OR Estado IS NULL').fetchall()
    elif tipo == 'labores':
        registros = conn.execute('SELECT Id, Nombre FROM Labores WHERE Estado != "1" OR Estado IS NULL').fetchall()
    elif tipo == 'equipos':
        registros = conn.execute('SELECT Id, Nombre FROM Equipos WHERE Estado != "1" OR Estado IS NULL').fetchall()
    else:
        conn.close()
        return jsonify([])
    
    conn.close()
    return jsonify([{'id': registro['Id'], 'nombre': registro['Nombre']} for registro in registros])

@app.route('/guardar_registro', methods=['POST'])
def guardar_registro():
    try:
        data = request.get_json()
        
        # Obtener los valores del formulario
        colaborador = data.get('colaborador')
        cliente = data.get('cliente')
        labor = data.get('labor')
        equipo = data.get('equipo')
        ubicacion = data.get('ubicacion')
        fecha = data.get('fecha')
        jornada = data.get('jornada')
        
        # Validar que todos los campos requeridos estén presentes
        if not all([colaborador, cliente, labor, equipo, ubicacion, fecha, jornada]):
            return jsonify({
                'success': False,
                'error': 'Todos los campos son requeridos'
            })
        
        conn = get_db_connection()
        
        # Insertar el nuevo registro
        conn.execute('''
            INSERT INTO Registro 
            (Colaborador, Cliente, Labor, Equipo, Ubicacion, Fecha, Jornada) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (colaborador, cliente, labor, equipo, ubicacion, fecha, jornada))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'error': 'Error al guardar el registro'
        })

@app.route('/informe')
def informe():
    return render_template('informe.html')

@app.route('/generar_informe', methods=['POST'])
def generar_informe():
    try:
        data = request.get_json()
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({
                'success': False,
                'error': 'Las fechas son requeridas'
            })
        
        conn = get_db_connection()
        
        # Consulta para obtener los registros con sus valores correspondientes
        registros = conn.execute('''
            SELECT 
                r.Fecha,
                r.Colaborador,
                r.Cliente,
                r.Labor,
                r.Equipo,
                r.Ubicacion,
                r.Jornada,
                l.Valor
            FROM Registro r
            JOIN Labores l ON r.Labor = l.Nombre AND r.Jornada = l.Jornada
            WHERE r.Fecha BETWEEN ? AND ?
            ORDER BY r.Fecha, r.Colaborador
        ''', (fecha_inicio, fecha_fin)).fetchall()
        
        # Procesar los resultados para el resumen
        totales_por_colaborador = {}
        registros_detallados = []
        
        for registro in registros:
            colaborador = registro['Colaborador']
            valor = registro['Valor'] or 0
            
            # Agregar al total por colaborador
            if colaborador in totales_por_colaborador:
                totales_por_colaborador[colaborador] += valor
            else:
                totales_por_colaborador[colaborador] = valor
            
            # Agregar a registros detallados
            registros_detallados.append({
                'fecha': registro['Fecha'],
                'colaborador': registro['Colaborador'],
                'cliente': registro['Cliente'],
                'labor': registro['Labor'],
                'equipo': registro['Equipo'],
                'ubicacion': registro['Ubicacion'],
                'jornada': registro['Jornada'],
                'valor': valor
            })
        
        # Convertir a lista de resultados
        resultados = [
            {'colaborador': colaborador, 'total': total}
            for colaborador, total in totales_por_colaborador.items()
        ]
        
        # Ordenar por colaborador
        resultados.sort(key=lambda x: x['colaborador'])
        
        conn.close()
        
        return jsonify({
            'success': True,
            'resultados': resultados,
            'registros': registros_detallados
        })
        
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'error': 'Error al generar el informe'
        })

@app.route('/exportar_registros')
def exportar_registros():
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return 'Las fechas son requeridas', 400
        
        conn = get_db_connection()
        
        # Consulta para obtener los registros
        registros = conn.execute('''
            SELECT 
                r.Fecha,
                r.Colaborador,
                r.Cliente,
                r.Labor,
                r.Equipo,
                r.Ubicacion,
                r.Jornada,
                l.Valor
            FROM Registro r
            JOIN Labores l ON r.Labor = l.Nombre AND r.Jornada = l.Jornada
            WHERE r.Fecha BETWEEN ? AND ?
            ORDER BY r.Fecha, r.Colaborador
        ''', (fecha_inicio, fecha_fin)).fetchall()
        
        conn.close()
        
        # Crear el contenido del CSV
        output = 'Fecha,Colaborador,Cliente,Labor,Equipo,Ubicación,Jornada,Valor\n'
        
        for registro in registros:
            # Formatear fecha
            fecha = registro['Fecha']
            # Formatear valor como moneda sin símbolo
            valor = '{:,.0f}'.format(registro['Valor'] if registro['Valor'] else 0)
            
            # Agregar fila al CSV, escapando comas en los campos
            output += f'"{fecha}","{registro["Colaborador"]}","{registro["Cliente"]}","{registro["Labor"]}",'
            output += f'"{registro["Equipo"]}","{registro["Ubicacion"]}","{registro["Jornada"]}","{valor}"\n'
        
        # Configurar la respuesta como un archivo CSV
        response = make_response(output)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=registros_{fecha_inicio}_{fecha_fin}.csv'
        
        return response
        
    except Exception as e:
        print(e)
        return 'Error al exportar los registros', 500

if __name__ == '__main__':
    app.run(debug=True) 