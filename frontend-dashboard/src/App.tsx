import { useState } from 'react';
import Papa from 'papaparse';

function App() {
  const [csvData, setCsvData] = useState<any[]>([]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (result) => {
        const data = result.data.map((row: any) => {
          // Normalize columns: ensure call_sid and timestamp are present
          return {
            phone_number: row.phone_number || '',
            call_sid: row.call_sid || '',
            summary: row.summary || '',
            action_items: row.action_items || '',
            timestamp: row.timestamp || '',
          };
        });
        setCsvData(data);
      },
    });
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-6 text-center">Call Summaries Dashboard</h1>
      <input
        type="file"
        accept=".csv"
        onChange={handleFileUpload}
        className="block mx-auto mb-4 border p-2 rounded"
      />

      {csvData.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="min-w-full border border-gray-300 bg-white text-sm">
            <thead>
              <tr className="bg-gray-200 text-left">
                <th className="border p-2">Phone Number</th>
                <th className="border p-2">CallSid</th>
                <th className="border p-2">Summary</th>
                <th className="border p-2">Action Items</th>
                <th className="border p-2">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {csvData.map((row, idx) => (
                <tr key={idx} className="hover:bg-gray-100">
                  <td className="border p-2">{row.phone_number}</td>
                  <td className="border p-2">{row.call_sid}</td>
                  <td className="border p-2">{row.summary}</td>
                  <td className="border p-2">{row.action_items}</td>
                  <td className="border p-2">{row.timestamp}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-center text-gray-500 mt-6">No data to display. Please upload a CSV file.</p>
      )}
    </div>
  );
}

export default App;
