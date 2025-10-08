import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import { AlphaVantageIncomeStatement } from '../types';

interface AlphaVantageIncomeChartProps {
  data: AlphaVantageIncomeStatement[];
  chartType: string;
}

const AlphaVantageIncomeChart: React.FC<AlphaVantageIncomeChartProps> = ({ data, chartType }) => {
  const formatCurrency = (value: number) => {
    if (value >= 1e9) {
      return `$${(value / 1e9).toFixed(2)}B`;
    } else if (value >= 1e6) {
      return `$${(value / 1e6).toFixed(2)}M`;
    }
    return `$${value.toFixed(2)}`;
  };

  const parseValue = (value?: string): number => {
    return value ? parseFloat(value) : 0;
  };

  const chartData = data.map((item) => ({
    date: item.fiscalDateEnding,
    revenue: parseValue(item.totalRevenue),
    grossProfit: parseValue(item.grossProfit),
    operatingIncome: parseValue(item.operatingIncome),
    netIncome: parseValue(item.netIncome),
    ebitda: parseValue(item.ebitda),
    costOfRevenue: parseValue(item.costOfRevenue),
    operatingExpenses: parseValue(item.operatingExpenses),
  })).reverse();

  const renderChart = () => {
    switch (chartType) {
      case 'revenue-trend':
        return (
          <ResponsiveContainer width="100%" height={500}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis tickFormatter={formatCurrency} />
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Legend />
              <Line type="monotone" dataKey="revenue" stroke="#8884d8" name="매출액" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'profit-comparison':
        return (
          <ResponsiveContainer width="100%" height={500}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis tickFormatter={formatCurrency} />
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Legend />
              <Bar dataKey="grossProfit" fill="#82ca9d" name="매출총이익" />
              <Bar dataKey="operatingIncome" fill="#8884d8" name="영업이익" />
              <Bar dataKey="netIncome" fill="#ffc658" name="순이익" />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'profit-margin':
        return (
          <ResponsiveContainer width="100%" height={500}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis tickFormatter={formatCurrency} />
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Legend />
              <Bar dataKey="revenue" fill="#8884d8" name="매출액" />
              <Bar dataKey="costOfRevenue" fill="#ff8042" name="매출원가" />
              <Bar dataKey="operatingExpenses" fill="#ffc658" name="영업비용" />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'all-metrics':
      default:
        return (
          <ResponsiveContainer width="100%" height={500}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis tickFormatter={formatCurrency} />
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Legend />
              <Bar dataKey="revenue" fill="#8884d8" name="매출액" />
              <Bar dataKey="grossProfit" fill="#82ca9d" name="매출총이익" />
              <Bar dataKey="operatingIncome" fill="#ffc658" name="영업이익" />
              <Bar dataKey="netIncome" fill="#ff8042" name="순이익" />
              <Bar dataKey="ebitda" fill="#a28cff" name="EBITDA" />
            </BarChart>
          </ResponsiveContainer>
        );
    }
  };

  return <div className="chart-container">{renderChart()}</div>;
};

export default AlphaVantageIncomeChart;
