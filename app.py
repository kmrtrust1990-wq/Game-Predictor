from flask import Flask, render_template, jsonify, request
import hashlib
import hmac
import random
import time

app = Flask(__name__)

def calculate_crash_point(server_seed, client_seed):
    hash_result = hmac.new(server_seed.encode(), client_seed.encode(), hashlib.sha256).hexdigest()
    number = int(hash_result[0:13], 16)
    
    if number % 100 == 0:
        return 1.00
    
    crash_point = (100 * 99 - number % 101) / (100 * 99 - (number % 2**52))
    return max(1.00, round(crash_point, 2))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate_rounds', methods=['POST'])
def generate_rounds():
    data = request.json
    num_rounds = int(data.get('rounds', 100))
    target_multiplier = float(data.get('target', 2.0))
    
    results = []
    wins = 0
    client_seed = "0000000000000000000fa3f65e43e4240d7d742265aa1d61c6586a1a4d46797a"
    
    for i in range(num_rounds):
        server_seed = hashlib.sha256(str(random.random() + time.time()).encode()).hexdigest()
        crash_point = calculate_crash_point(server_seed, client_seed)
        
        is_win = crash_point >= target_multiplier
        if is_win:
            wins += 1
            
        results.append({
            "round": i + 1,
            "crash_point": crash_point,
            "result": "Win" if is_win else "Loss"
        })
    
    accuracy = (wins / num_rounds) * 100
    return jsonify({
        "success": True,
        "accuracy": round(accuracy, 2),
        "total_wins": wins,
        "total_losses": num_rounds - wins,
        "data": results
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
