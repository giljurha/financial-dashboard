import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { financialApi } from './services/api';
import IncomeStatementChart from './components/IncomeStatementChart';
import { IncomeStatementData } from './types';

function App() {
  const [symbol, setSymbol] = useState<string>('AAPL');
  const [searchSymbol, setSearchSymbol] = useState<string>('AAPL');
  const [chartType, setChartType] = useState<string>('all-metrics');

  const { data, isLoading, error, refetch } = useQuery<IncomeStatementData[]>(
    ['incomeStatement', searchSymbol],
    () => financialApi.getIncomeStatement(searchSymbol),
    {
      enabled: !!searchSymbol,
    }
  );

  const handleSearch = () => {
    setSearchSymbol(symbol);
    refetch();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="App">
      <header className="header">
        <h1>재무 대시보드</h1>
        <p>기업의 손익계산서 데이터를 인터랙티브 차트로 분석하세요</p>
      </header>

      <div className="container">
        <>
          <div className="search-container">
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

        {isLoading && <div className="loading">손익계산서 데이터를 불러오는 중...</div>}

        {error && (
          <div className="error">
            손익계산서 데이터를 불러오는 중 오류가 발생했습니다. 주식 심볼을 확인하고 다시 시도해주세요.
          </div>
        )}

        {data && data.length > 0 && (
          <div>
            <h2>{searchSymbol} 손익계산서</h2>
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
            <IncomeStatementChart data={data} chartType={chartType} />
          </div>
        )}

        {data && data.length === 0 && (
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