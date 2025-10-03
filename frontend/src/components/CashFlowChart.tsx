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
import { CashFlowData } from '../types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface CashFlowChartProps {
  data: CashFlowData[];
}

const CashFlowChart: React.FC<CashFlowChartProps> = ({ data }) => {
  const chartData = {
    labels: data.map(item => item.fiscalYear),
    datasets: [
      {
        label: 'Operating Cash Flow',
        data: data.map(item => item.operatingCashFlow / 1000000), // Convert to millions
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
      {
        label: 'Free Cash Flow',
        data: data.map(item => item.freeCashFlow / 1000000), // Convert to millions
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1,
      },
      {
        label: 'Net Income',
        data: data.map(item => item.netIncome / 1000000), // Convert to millions
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
        text: 'Cash Flow Analysis (in Millions USD)',
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
          text: 'Fiscal Year',
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

export default CashFlowChart;