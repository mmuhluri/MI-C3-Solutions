from flask import Flask, request, jsonify, render_template
from datetime import datetime, timezone
import socket

app = Flask(__name__)

def get_seconds_difference(t1, t2):
    fmt = "%a %d %b %Y %H:%M:%S %z"
    dt1 = datetime.strptime(t1, fmt)
    dt2 = datetime.strptime(t2, fmt)
    dt1_utc = dt1.astimezone(timezone.utc)
    dt2_utc = dt2.astimezone(timezone.utc)
    delta = dt1_utc - dt2_utc
    return abs(int(delta.total_seconds()))

def process_input(data):
    lines = [line.strip() for line in data.split('\n') if line.strip()]
    if not lines:
        return None, "No input provided"
    
    try:
        T = int(lines[0])
    except ValueError:
        return None, "Invalid number of test cases"
    
    if len(lines) < 1 + 2 * T:
        return None, "Insufficient input lines"
    
    results = []
    index = 1
    for _ in range(T):
        try:
            t1 = lines[index]
            t2 = lines[index + 1]
            results.append(str(get_seconds_difference(t1, t2)))
            index += 2
        except IndexError:
            return None, "Invalid input format"
    return results, None

@app.route('/', methods=['GET', 'POST'])
def index():
    node_id = socket.gethostname()
    if request.method == 'POST':
        input_data = request.form.get('input_data', '')
        results, error = process_input(input_data)
        return render_template('index.html', 
                             results=results,
                             error=error,
                             node_id=node_id,
                             input_data=input_data)
    return render_template('index.html', node_id=node_id)

@app.route('/compute', methods=['POST'])
def compute():
    data = request.get_data(as_text=True)
    results, error = process_input(data)
    node_id = socket.gethostname()
    
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"id": node_id, "result": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)