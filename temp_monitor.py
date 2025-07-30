from flask import Flask, render_template, jsonify
import subprocess
import json
from datetime import datetime
import os

app = Flask(__name__)


def get_cpu_temperature():
    """Obtiene la temperatura de la CPU"""
    try:
        # Método principal para Raspberry Pi
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read().strip()) / 1000.0
        return round(temp, 1)
    except:
        try:
            # Método alternativo usando vcgencmd
            result = subprocess.run(['vcgencmd', 'measure_temp'],
                                    capture_output=True, text=True)
            temp_str = result.stdout.strip()
            temp = float(temp_str.split('=')[1].split("'")[0])
            return round(temp, 1)
        except:
            return None


def get_system_info():
    """Obtiene información adicional del sistema"""
    try:
        # CPU usage
        cpu_usage = subprocess.run(['top', '-bn1'],
                                   capture_output=True, text=True)
        cpu_line = [line for line in cpu_usage.stdout.split('\n')
                    if 'Cpu(s)' in line][0]
        cpu_percent = cpu_line.split(',')[0].split(':')[1].strip().split('%')[0]

        # Memory usage
        mem_info = subprocess.run(['free', '-m'],
                                  capture_output=True, text=True)
        mem_lines = mem_info.stdout.split('\n')[1].split()
        total_mem = int(mem_lines[1])
        used_mem = int(mem_lines[2])
        mem_percent = round((used_mem / total_mem) * 100, 1)

        # Uptime
        uptime = subprocess.run(['uptime', '-p'],
                                capture_output=True, text=True)

        return {
            'cpu_usage': f"{cpu_percent}%",
            'memory_usage': f"{mem_percent}%",
            'memory_used': f"{used_mem}MB",
            'memory_total': f"{total_mem}MB",
            'uptime': uptime.stdout.strip()
        }
    except:
        return {
            'cpu_usage': 'N/A',
            'memory_usage': 'N/A',
            'memory_used': 'N/A',
            'memory_total': 'N/A',
            'uptime': 'N/A'
        }


@app.route('/')
def index():
    """Página principal"""
    temp = get_cpu_temperature()
    system_info = get_system_info()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return render_template('index.html',
                           temperature=temp,
                           system_info=system_info,
                           current_time=current_time)


@app.route('/api/temperature')
def api_temperature():
    """API endpoint para obtener solo la temperatura"""
    temp = get_cpu_temperature()
    return jsonify({
        'temperature': temp,
        'timestamp': datetime.now().isoformat(),
        'unit': 'Celsius'
    })


@app.route('/api/system')
def api_system():
    """API endpoint para obtener toda la información del sistema"""
    temp = get_cpu_temperature()
    system_info = get_system_info()

    return jsonify({
        'temperature': temp,
        'system_info': system_info,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # Crear directorio de templates si no existe
    if not os.path.exists('templates'):
        os.makedirs('templates')

    app.run(host='0.0.0.0', port=5000, debug=True)
