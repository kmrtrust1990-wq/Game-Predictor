from flask import Flask, jsonify, request, render_template_string
import hashlib
import hmac
import random
import time
import os

app = Flask(__name__)

# ফ্রন্টএন্ড ডিজাইন (HTML/JS) সরাসরি কোডের ভেতরে যুক্ত করা হয়েছে
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crash Algorithm Test Server</title>
    <link href="https://jsdelivr.net" rel="stylesheet">
    <script src="https://jsdelivr.net"></script>
</head>
<body class="bg-dark text-light p-4">
    <div class="container bg-secondary bg-opacity-25 rounded p-4 shadow">
        <h2 class="text-center text-warning mb-4">Aviator RNG Algorithm Simulator</h2>
        
        <div class="row g-3">
            <div class="col-md-4">
                <label class="form-label">কতগুলো রাউন্ড জেনারেট করবেন?</label>
                <input type="number" id="roundsInput" class="form-control bg-dark text-light" value="500">
            </div>
            <div class="col-md-4">
                <label class="form-label">আপনার টার্গেট প্রেডিকশন ভ্যালু (যেমন: ২.০০x)</label>
                <input type="number" step="0.1" id="targetInput" class="form-control bg-dark text-light" value="2.0">
            </div>
            <div class="col-md-4 d-flex align-items-end">
                <button onclick="runTest()" class="btn btn-success w-100 fw-bold">সিমুলেশন রান করুন</button>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-6">
                <h4>স্ট্যাটিস্টিক্স ও একুরেসি</h4>
                <div class="card bg-dark text-light p-3">
                    <p>মোট উইন (টার্গেট বা তার বেশি): <span id="winCount" class="text-success fw-bold">-</span></p>
                    <p>মোট লস (টার্গেটের নিচে ক্র্যাশ): <span id="lossCount" class="text-danger fw-bold">-</span></p>
                    <p>আপনার স্ট্র্যাটেজির আসল একুরেসি: <span id="accuracyPercent" class="text-warning fw-bold">-</span></p>
                </div>
            </div>
            <div class="col-md-6">
                <canvas id="resultChart" style="max-height: 200px;"></canvas>
            </div>
        </div>

        <div class="mt-4">
            <h4>লাইভ জেনারেটেড ডেটা লগ (সর্বশেষ ৫০টি রাউন্ড)</h4>
            <div class="table-responsive" style="max-height: 300px; overflow-y: auto;">
                <table class="table table-dark table-striped text-center">
                    <thead>
                        <tr>
                            <th>রাউন্ড নং</th>
                            <th>ক্র্যাশ পয়েন্ট</th>
                            <th>আপনার প্রেডিকশন রেজাল্ট</th>
                        </tr>
                    </thead>
                    <tbody id="dataTableBody"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let myChart;
        function runTest() {
            const rounds = document.getElementById('roundsInput').value;
            const target = document.getElementById('targetInput').value;

            fetch('/api/generate_rounds', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rounds: rounds, target: target })
            })
            .then(res => res.json())
            .then(resData => {
                document.getElementById('winCount').innerText = resData.total_wins;
                document.getElementById('lossCount').innerText = resData.total_losses;
                document.getElementById('accuracyPercent').innerText = resData.accuracy + "%";

                const tbody = document.getElementById('dataTableBody');
                tbody.innerHTML = "";
                resData.data.slice(-50).reverse().forEach(item => {
                    tbody.innerHTML += `<tr>
                        <td>${item.round}</td>
                        <td class="${item.crash_point >= 2 ? 'text-info' : 'text-danger'}">${item.crash_point}x</td>
                        <td><span class="badge ${item.result === 'Win' ? 'bg-success' : 'bg-danger'}">${item.result}</span></td>
                    </tr>`;
                });

                if (myChart) myChart.destroy();
                const ctx = document.getElementById('resultChart').getContext('2d');
                myChart = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: ['Win', 'Loss'],
                        datasets: [{
                            data: [resData.total_wins, resData.total_losses],
                            backgroundColor: ['#198754', '#dc3545']
                        }]
                    }
                });
            });
        }
    </script>
</body>
</html>
"""

def calculate_crash_point(server_seed, client_seed):
    hash_result = hmac.new(server_seed.encode(), client_seed.encode(), hashlib.sha256).hexdigest()
    number = int(hash_result[0:13], 16)
    if number % 100 == 0:
        return 1.00
    crash_point = (100 * 99 - number % 101) / (100 * 99 - (number % 2**52))
    return max(1.00, round(crash_point, 2))

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
