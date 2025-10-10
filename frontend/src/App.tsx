import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { financialApi, alphaVantageApi } from './services/api';
import IncomeStatementChart from './components/IncomeStatementChart';
import AlphaVantageIncomeChart from './components/AlphaVantageIncomeChart';
import { IncomeStatementData, AlphaVantageIncomeStatementResponse } from './types';
import { useTheme } from './context/ThemeContext';

function App() {
  const { theme, toggleTheme } = useTheme();
  const [symbol, setSymbol] = useState<string>('AAPL');
  const [searchSymbol, setSearchSymbol] = useState<string>('AAPL');
  const [chartType, setChartType] = useState<string>('all-metrics');
  const [apiSource, setApiSource] = useState<string>('financial-modeling-prep');

  const { data, isLoading, error, refetch } = useQuery<IncomeStatementData[]>(
    ['incomeStatement', searchSymbol],
    () => financialApi.getIncomeStatement(searchSymbol),
    {
      enabled: !!searchSymbol && apiSource === 'financial-modeling-prep',
    }
  );

  const { data: alphaData, isLoading: alphaLoading, error: alphaError, refetch: alphaRefetch } = useQuery<AlphaVantageIncomeStatementResponse>(
    ['alphaVantageIncome', searchSymbol],
    () => alphaVantageApi.getIncomeStatement(searchSymbol),
    {
      enabled: !!searchSymbol && apiSource === 'alphavantage',
    }
  );

  const handleSearch = () => {
    setSearchSymbol(symbol);
    if (apiSource === 'financial-modeling-prep') {
      refetch();
    } else {
      alphaRefetch();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="App">
      <header className="header">
        <div className="header-content">
          <div className="header-title">
            <h1>원하는 주식을 검색해보세요</h1>
            <p>기업의 손익계산서 데이터를 차트로 보여드립니다</p>
          </div>
        </div>
        <button className="theme-toggle" onClick={toggleTheme}>
          <span className="theme-icon">{theme === 'light' ? '🌙' : '☀️'}</span>
          <span>{theme === 'light' ? '다크 모드' : '라이트 모드'}</span>
        </button>
      </header>

      <div className="container">
        <>
          <div className="search-container">
            <div className="api-source-selector">
              <label htmlFor="api-source-select">데이터 소스: </label>
              <select
                id="api-source-select"
                value={apiSource}
                onChange={(e) => setApiSource(e.target.value)}
                className="api-source-select"
              >
                <option value="financial-modeling-prep">Financial Modeling Prep</option>
                <option value="alphavantage">AlphaVantage</option>
              </select>
            </div>
            <input
              type="text"
              className="search-input"
              placeholder="주식 심볼을 입력하세요 (예: AAPL)"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              onKeyPress={handleKeyPress}
            />
            <button className="search-button" onClick={handleSearch}>
              검색
            </button>
          </div>

          {apiSource === 'financial-modeling-prep' && isLoading && <div className="loading">손익계산서 데이터를 불러오는 중...</div>}
          {apiSource === 'alphavantage' && alphaLoading && <div className="loading">손익계산서 데이터를 불러오는 중...</div>}

          {apiSource === 'financial-modeling-prep' && error && !isLoading && (
            <div className="error">
              손익계산서 데이터를 불러오는 중 오류가 발생했습니다. 주식 심볼을 확인하고 다시 시도해주세요.
            </div>
          )}
          {apiSource === 'alphavantage' && alphaError && !alphaLoading && (
            <div className="error">
              손익계산서 데이터를 불러오는 중 오류가 발생했습니다. 주식 심볼을 확인하고 다시 시도해주세요.
            </div>
          )}

          {apiSource === 'financial-modeling-prep' && data && data.length > 0 && (
            <div>
              <div className="chart-header">
                <h2>{searchSymbol} 손익계산서 (Financial Modeling Prep)</h2>
                <div className="chart-controls">
                  <label htmlFor="chart-type-select">차트 유형: </label>
                  <select
                    id="chart-type-select"
                    value={chartType}
                    onChange={(e) => setChartType(e.target.value)}
                    className="chart-type-select"
                  >
                    <option value="all-metrics">전체 지표</option>
                    <option value="revenue-trend">매출 추이</option>
                    <option value="profit-comparison">수익성 비교</option>
                    <option value="profit-margin">수익 구성</option>
                  </select>
                </div>
              </div>
              <IncomeStatementChart data={data} chartType={chartType} />
            </div>
          )}

          {apiSource === 'alphavantage' && alphaData && alphaData.annualReports && alphaData.annualReports.length > 0 && (
            <div>
              <div className="chart-header">
                <h2>{searchSymbol} 손익계산서 (AlphaVantage)</h2>
                <div className="chart-controls">
                  <label htmlFor="chart-type-select">차트 유형: </label>
                  <select
                    id="chart-type-select"
                    value={chartType}
                    onChange={(e) => setChartType(e.target.value)}
                    className="chart-type-select"
                  >
                    <option value="all-metrics">전체 지표</option>
                    <option value="revenue-trend">매출 추이</option>
                    <option value="profit-comparison">수익성 비교</option>
                    <option value="profit-margin">수익 구성</option>
                  </select>
                </div>
              </div>
              <AlphaVantageIncomeChart data={alphaData.annualReports} chartType={chartType} />
            </div>
          )}

          {apiSource === 'financial-modeling-prep' && data && data.length === 0 && (
            <div className="error">
              심볼 {searchSymbol}에 대한 손익계산서 데이터를 찾을 수 없습니다.
            </div>
          )}

          {apiSource === 'alphavantage' && alphaData && (!alphaData.annualReports || alphaData.annualReports.length === 0) && (
            <div className="error">
              심볼 {searchSymbol}에 대한 손익계산서 데이터를 찾을 수 없습니다.
            </div>
          )}
        </>
      </div>
    </div>
  );
}

export default App;