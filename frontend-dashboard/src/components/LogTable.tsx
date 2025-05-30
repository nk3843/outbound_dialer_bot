import React, { useEffect, useState } from 'react';
import Papa from 'papaparse';

type LogRow = {
  phone_number: string;
  question?: string;
  answer?: string;
  summary?: string;
  action_items?: string;
  timestamp?: string;
};

const LogTable: React.FC = () => {
  const [data, setData] = useState<LogRow[]>([]);

  useEffect(() => {
    fetch('/logs/responses.csv')
      .then(response => response.text())
      .then(csvText => {
        const parsed = Papa.parse<LogRow>(csvText, { header: true });
        setData(parsed.data);
      });
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Call Log Dashboard</h1>
      <table className="table-auto border-collapse border border-gray-300 w-full">
        <thead>
          <tr>
            <th className="border p-2">Phone</th>
            <th className="border p-2">Question</th>
            <th className="border p-2">Answer</th>
            <th className="border p-2">Summary</th>
            <th className="border p-2">Action Items</th>
            <th className="border p-2">Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx}>
              <td className="border p-2">{row.phone_number}</td>
              <td className="border p-2">{row.question}</td>
              <td className="border p-2">{row.answer}</td>
              <td className="border p-2">{row.summary}</td>
              <td className="border p-2">{row.action_items}</td>
              <td className="border p-2">{row.timestamp}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default LogTable;
