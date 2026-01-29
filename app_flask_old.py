from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    hostname = os.environ.get('HOSTNAME', 'unknown')
    return f'''
    <h1>¡Hola desde Docker!</h1>
    <p>Container ID: {hostname}</p>
    <p>Esta aplicación está corriendo en un contenedor Docker 🐳</p>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    