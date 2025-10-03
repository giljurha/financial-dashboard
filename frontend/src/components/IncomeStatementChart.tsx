import React from 'react';
import { Bar, Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { IncomeStatementData } from '../types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface IncomeStatementChartProps {
  data: IncomeStatementData[];
  chartType: string;
}

const IncomeStatementChart: React.FC<IncomeStatementChartProps> = ({ data, chartType }) => {
  if (!data || data.length === 0) {
    return <div>손익계산서 데이터가 없습니다</div>;
  }

  const years = data.map(item => item.fiscalYear).reverse();
  const revenue = data.map(item => item.revenue ? item.revenue / 1000000 : 0).reverse();
  const grossProfit = data.map(item => item.grossProfit ? item.grossProfit / 1000000 : 0).reverse();
  const operatingIncome = data.map(item => item.operatingIncome ? item.operatingIncome / 1000000 : 0).reverse();
  const netIncome = data.map(item => item.netIncome ? item.netIncome / 1000000 : 0).reverse();

  const getChartData = () => {
    const baseColors = [
      'rgba(54, 162, 235, 0.6)',
      'rgba(75, 192, 192, 0.6)',
      'rgba(255, 206, 86, 0.6)',
      'rgba(153, 102, 255, 0.6)'
    ];

    const borderColors = [
      'rgba(54, 162, 235, 1)',
      'rgba(75, 192, 192, 1)',
      'rgba(255, 206, 86, 1)',
      'rgba(153, 102, 255, 1)'
    ];

    switch (chartType) {
      case 'revenue-trend':
        return {
          labels: years,
          datasets: [{
            label: '매출 (백만원)',
            data: revenue,
            backgroundColor: baseColors[0],
            borderColor: borderColors[0],
            borderWidth: 2,
            fill: false,
          }]
        };

      case 'profit-comparison':
        return {
          labels: years,
          datasets: [
            {
              label: '매출총이익 (백만원)',
              data: grossProfit,
              backgroundColor: baseColors[1],
              borderColor: borderColors[1],
              borderWidth: 1,
            },
            {
              label: '영업이익 (백만원)',
              data: operatingIncome,
              backgroundColor: baseColors[2],
              borderColor: borderColors[2],
              borderWidth: 1,
            },
            {
              label: '순이익 (백만원)',
              data: netIncome,
              backgroundColor: baseColors[3],
              borderColor: borderColors[3],
              borderWidth: 1,
            }
          ]
        };

      case 'profit-margin':
        const latestData = data[0];
        return {
          labels: ['매출총이익', '영업이익', '순이익'],
          datasets: [{
            data: [
              latestData?.grossProfit ? latestData.grossProfit / 1000000 : 0,
              latestData?.operatingIncome ? latestData.operatingIncome / 1000000 : 0,
              latestData?.netIncome ? latestData.netIncome / 1000000 : 0
            ],
            backgroundColor: [baseColors[1], baseColors[2], baseColors[3]],
            borderColor: [borderColors[1], borderColors[2], borderColors[3]],
            borderWidth: 1,
          }]
        };

      default: // 'all-metrics'
        return {
          labels: years,
          datasets: [
            {
              label: '매출 (백만원)',
              data: revenue,
              backgroundColor: baseColors[0],
              borderColor: borderColors[0],
              borderWidth: 1,
            },
            {
              label: '매출총이익 (백만원)',
              data: grossProfit,
              backgroundColor: baseColors[1],
              borderColor: borderColors[1],
              borderWidth: 1,
            },
            {
              label: '영업이익 (백만원)',
              data: operatingIncome,
              backgroundColor: baseColors[2],
              borderColor: borderColors[2],
              borderWidth: 1,
            },
            {
              label: '순이익 (백만원)',
              data: netIncome,
              backgroundColor: baseColors[3],
              borderColor: borderColors[3],
              borderWidth: 1,
            },
          ]
        };
    }
  };

  const chartData = getChartData();

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        align: 'center' as const,
        labels: {
          padding: 20,
          usePointStyle: true,
        },
      },
      title: {
        display: true,
        text: '손익계산서 분석',
        align: 'center' as const,
        font: {
          size: 16,
          weight: 'bold' as const,
        },
        padding: 20,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: '금액 (백만 USD)',
          align: 'center' as const,
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
      },
      x: {
        title: {
          display: true,
          text: '회계연도',
          align: 'center' as const,
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
      },
    },
    layout: {
      padding: {
        top: 10,
        bottom: 10,
        left: 10,
        right: 10,
      },
    },
  };

  const renderChart = () => {
    switch (chartType) {
      case 'revenue-trend':
        return <Line data={chartData} options={options} />;
      case 'profit-margin':
        return <Doughnut data={chartData} options={options} />;
      default:
        return <Bar data={chartData} options={options} />;
    }
  };

  return (
    <div
      className="chart-container"
      style={{
        width: '100%',
        height: '500px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative'
      }}
    >
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        {renderChart()}
      </div>
    </div>
  );
};

export default IncomeStatementChart;