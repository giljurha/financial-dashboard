import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { BalanceSheetData } from '../types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface BalanceSheetChartProps {
  data: BalanceSheetData[];
}

const BalanceSheetChart: React.FC<BalanceSheetChartProps> = ({ data }) => {
  const chartData = {
    labels: data.map(item => item.calendarYear),
    datasets: [
      {
        label: 'Total Assets',
        data: data.map(item => item.totalAssets / 1000000), // Convert to millions
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
      {
        label: 'Total Current Assets',
        data: data.map(item => item.totalCurrentAssets / 1000000), // Convert to millions
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1,
      },
      {
        label: 'Cash and Cash Equivalents',
        data: data.map(item => item.cashAndCashEquivalents / 1000000), // Convert to millions
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Balance Sheet Analysis (in Millions USD)',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Amount (Millions USD)',
        },
      },
      x: {
        title: {
          display: true,
          text: 'Year',
        },
      },
    },
  };

  return (
    <div className="chart-container">
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default BalanceSheetChart;