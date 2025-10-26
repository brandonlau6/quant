import React, { useState } from 'react';

interface Trade {
  date: string;
  signal: string;
  price: number;
  strategy: string;
}

interface Metric {
  Metric: string;
  Value: number;
}

const API_URL = "http://localhost:8000/api/v1";

const App: React.FC = () => {
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [ticker, setTicker] = useState('');
  const [strategy, setStrategy] = useState('');
  const [buy, setBuy] = useState<number | ''>('');
  const [sell, setSell] = useState<number | ''>('');

  const [trades, setTrades] = useState<Trade[]>([]);
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // Pagination state
  const [page, setPage] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const size = 10;

  // Normalize backend data into trade objects
  const normalizeTrades = (data: any): Trade[] => {
    if (!data || !data.date) return [];
    const keys = Object.keys(data.date);
    return keys.map((k) => ({
      date: data.date[k],
      signal: data.signal[k],
      price: data.price[k],
      strategy: data.strategy[k],
    }));
  };

  // Fetch trades by page index
  const fetchTrades = async (newPage = 0) => {
    const offset = newPage * size;
    const res = await fetch(
      `${API_URL}/getBacktest?start=${start}&end=${end}&ticker=${ticker}&strategy=${strategy}&size=${size}&offset=${offset}`
    );
    const data = await res.json();
    const parsed = normalizeTrades(data);
    setTrades(parsed);
    setHasNext(parsed.length === size); // disable "Next" if fewer than size results
  };

  const handleBacktest = async () => {
    if (!start || !end || !ticker || !strategy || buy === '' || sell === '') {
      alert("Please fill out all fields.");
      return;
    }

    setLoading(true);
    setMessage('');
    setTrades([]);
    setMetrics([]);
    setPage(0);

    try {
      // Run the backtest first
      const backtestRes = await fetch(`${API_URL}/backtest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start, end, ticker, strategy, buy, sell }),
      });

      const backtestText = await backtestRes.text();
      setMessage(backtestText);

      if (backtestRes.ok) {
        // Fetch first trade page
        await fetchTrades(0);

        // Fetch metrics
        const metricsRes = await fetch(`${API_URL}/metrics`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ start, end, ticker, strategy }),
        });
        const metricsData = await metricsRes.json();
        setMetrics(metricsData);
      }
    } catch (err) {
      console.error(err);
      setMessage('Error contacting API');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    if (!hasNext) return;
    const nextPage = page + 1;
    await fetchTrades(nextPage);
    setPage(nextPage);
  };

  const handlePrev = async () => {
    if (page === 0) return;
    const prevPage = page - 1;
    await fetchTrades(prevPage);
    setPage(prevPage);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8 flex flex-col items-center">
      <h1 className="text-2xl font-bold mb-6">Backtesting Dashboard</h1>

      {/* Input Form */}
      <div className="bg-white shadow-lg rounded-2xl p-6 w-full max-w-3xl mb-8">
        <div className="grid grid-cols-2 gap-4 mb-4">
          <input type="date" value={start} onChange={(e) => setStart(e.target.value)} className="border rounded-lg p-2" />
          <input type="date" value={end} onChange={(e) => setEnd(e.target.value)} className="border rounded-lg p-2" />
          <input type="text" placeholder="Ticker (e.g. AAPL)" value={ticker} onChange={(e) => setTicker(e.target.value)} className="border rounded-lg p-2" />
          <input type="text" placeholder="Strategy Name" value={strategy} onChange={(e) => setStrategy(e.target.value)} className="border rounded-lg p-2" />
          <input type="number" placeholder="Buy Threshold" value={buy} onChange={(e) => setBuy(parseFloat(e.target.value))} className="border rounded-lg p-2" />
          <input type="number" placeholder="Sell Threshold" value={sell} onChange={(e) => setSell(parseFloat(e.target.value))} className="border rounded-lg p-2" />
        </div>

        <button
          onClick={handleBacktest}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg w-full"
        >
          {loading ? 'Running Backtest...' : 'Run Backtest'}
        </button>

        {message && <p className="text-center text-sm mt-3 text-gray-700">{message}</p>}
      </div>

      {/* Trades Table */}
      {trades.length > 0 && (
        <div className="bg-white shadow-lg rounded-2xl p-6 w-full max-w-4xl mb-8 overflow-x-auto">
          <h2 className="text-xl font-semibold mb-4">Trade Results</h2>
          <table className="w-full text-sm border border-gray-200 rounded-lg">
            <thead>
              <tr className="bg-gray-100 border-b">
                <th className="p-2 text-left">Date</th>
                <th className="p-2 text-left">Signal</th>
                <th className="p-2 text-left">Price</th>
                <th className="p-2 text-left">Strategy</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((trade, i) => (
                <tr key={i} className="border-b hover:bg-gray-50">
                  <td className="p-2">{trade.date}</td>
                  <td className="p-2">{trade.signal}</td>
                  <td className="p-2">{trade.price.toFixed(2)}</td>
                  <td className="p-2">{trade.strategy}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination Controls */}
          <div className="flex justify-between items-center mt-4">
            <button
              onClick={handlePrev}
              disabled={page === 0}
              className={`px-4 py-2 rounded-lg ${
                page === 0 ? 'bg-gray-300 cursor-not-allowed' : 'bg-gray-200 hover:bg-gray-300'
              }`}
            >
              ← Previous
            </button>
            <span className="text-sm text-gray-600">Page {page + 1}</span>
            <button
              onClick={handleNext}
              disabled={!hasNext}
              className={`px-4 py-2 rounded-lg ${
                !hasNext ? 'bg-gray-300 cursor-not-allowed' : 'bg-gray-200 hover:bg-gray-300'
              }`}
            >
              Next →
            </button>
          </div>
        </div>
      )}

      {/* Metrics Table */}
      {metrics.length > 0 && (
        <div className="bg-white shadow-lg rounded-2xl p-6 w-full max-w-2xl">
          <h2 className="text-xl font-semibold mb-4">Metrics</h2>
          <table className="w-full text-sm border border-gray-200 rounded-lg">
            <thead>
              <tr className="bg-gray-100 border-b">
                <th className="p-2 text-left">Metric</th>
                <th className="p-2 text-left">Value</th>
              </tr>
            </thead>
            <tbody>
              {metrics.map((m, i) => (
                <tr key={i} className="border-b hover:bg-gray-50">
                  <td className="p-2 font-medium">{m.Metric}</td>
                  <td className="p-2">{Number.isFinite(m.Value) ? m.Value.toFixed(4) : m.Value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default App;
