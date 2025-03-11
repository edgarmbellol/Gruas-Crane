from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/menu', methods=['POST', 'GET'])
def menu():
    if request.method == 'POST':
        if 'Trabajadores' in request.form:
            return redirect(url_for('Trabajadores'))
        elif 'Clientes' in request.form:
            return redirect(url_for('clientes'))
        elif 'Labores' in request.form:
            return redirect(url_for('productos'))
        elif 'Equipos' in request.form:
            return redirect(url_for('productos'))
        elif 'Sueldos' in request.form:
            return redirect(url_for('ventas'))
        elif 'Informe' in request.form:
            return redirect(url_for('reportes'))
    else:
        return render_template('menu.html')

@app.route('/submit', methods=['POST'])
def submit():     
    if 'button1' in request.form:
        return "Button 1 was pressed"
    elif 'button2' in request.form:
        return "Button 2 was pressed"
    elif 'button3' in request.form:
        return "Button 3 was pressed"
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)