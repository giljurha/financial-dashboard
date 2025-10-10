import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { financialApi, alphaVantageApi } from './services/api';
import IncomeStatementChart from './components/IncomeStatementChart';
import AlphaVantageIncomeChart from './components/AlphaVantageIncomeChart';
import CustomSelect from './components/CustomSelect';
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
            <CustomSelect
              label="데이터 소스:"
              options={[
                { value: 'financial-modeling-prep', label: 'Financial Modeling Prep' },
                { value: 'alphavantage', label: 'AlphaVantage' }
              ]}
              value={apiSource}
              onChange={setApiSource}
              className="api-source-selector"
            />
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
                <CustomSelect
                  label="차트 유형:"
                  options={[
                    { value: 'all-metrics', label: '전체 지표' },
                    { value: 'revenue-trend', label: '매출 추이' },
                    { value: 'profit-comparison', label: '수익성 비교' },
                    { value: 'profit-margin', label: '수익 구성' }
                  ]}
                  value={chartType}
                  onChange={setChartType}
                  className="chart-controls"
                />
              </div>
              <IncomeStatementChart data={data} chartType={chartType} />
            </div>
          )}

          {apiSource === 'alphavantage' && alphaData && alphaData.annualReports && alphaData.annualReports.length > 0 && (
            <div>
              <div className="chart-header">
                <h2>{searchSymbol} 손익계산서 (AlphaVantage)</h2>
                <CustomSelect
                  label="차트 유형:"
                  options={[
                    { value: 'all-metrics', label: '전체 지표' },
                    { value: 'revenue-trend', label: '매출 추이' },
                    { value: 'profit-comparison', label: '수익성 비교' },
                    { value: 'profit-margin', label: '수익 구성' }
                  ]}
                  value={chartType}
                  onChange={setChartType}
                  className="chart-controls"
                />
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