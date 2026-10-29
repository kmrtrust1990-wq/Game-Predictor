HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mobile Game & Dashboard</title>
    <link href="https://jsdelivr.net" rel="stylesheet">
    <script src="https://jsdelivr.net"></script>
    <style>
        body, html { margin: 0; padding: 0; height: 100%; background: #111; color: #fff; overflow-x: hidden; }
        .game-container { width: 100%; height: 50vh; border-bottom: 3px solid #ffc107; }
        .game-frame { width: 100%; height: 100%; border: none; }
        .dashboard-container { width: 100%; height: 50vh; overflow-y: auto; padding: 15px; }
    </style>
</head>
<body>

    <!-- উপরের অংশ: এখানে গেমের সাইট লোড হবে -->
    <div class="game-container">
        <!-- 'https://999bd.com' এর জায়গায় আপনার গেমের আসল লিংকটি বসিয়ে দিন -->
        <iframe src="https://999bd.com/" class="game-frame"></iframe>
    </div>

    <!-- নিচের অংশ: আপনার তৈরি অ্যালগরিদম ড্যাশবোর্ড -->
    <div class="dashboard-container">
        <h4 class="text-warning text-center mb-3">RNG Algorithm Simulator</h4>
        
        <div class="row g-2">
            <div class="col-6">
                <label class="form-label small">রাউন্ড সংখ্যা</label>
                <input type="number" id="roundsInput" class="form-control form-control-sm bg-dark text-light" value="100">
            </div>
            <div class="col-6">
                <label class="form-label small">টার্গেট ভ্যালু</label>
                <input type="number" step="0.1" id="targetInput" class="form-control form-control-sm bg-dark text-light" value="2.0">
            </div>
            <div class="col-12 mt-2">
                <button onclick="runTest()" class="btn btn-success btn-sm w-100 fw-bold">সিমুলেশন রান করুন</button>
            </div>
        </div>

        <div class="row mt-3 bg-secondary bg-opacity-25 rounded p-2 g-0">
            <div class="col-6 small">
                <p class="mb-1">উইন: <span id="winCount" class="text-success fw-bold">-</span></p>
                <p class="mb-1">লস: <span id="lossCount" class="text-danger fw-bold">-</span></p>
                <p class="mb-0">একুরেসি: <span id="accuracyPercent" class="text-warning fw-bold">-</span></p>
            </div>
            <div class="col-6 d-flex align-items-center">
                <canvas id="resultChart" style="max-height: 80px;"></canvas>
            </div>
        </div>

        <div class="mt-3">
            <h6 class="small">সর্বশেষ ডেটা লগ</h6>
            <div class="table-responsive" style="max-height: 150px;">
                <table class="table table-sm table-dark table-striped text-center small" style="font-size: 12px;">
                    <thead>
                        <tr>
                            <th>রাউন্ড</th>
                            <th>পয়েন্ট</th>
                            <th>রেজাল্ট</th>
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
                resData.data.slice(-20).reverse().forEach(item => {
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
                    },
                    options: { plugins: { legend: { display: false } } }
                });
            });
        }
    </script>
</body>
</html>
"""
