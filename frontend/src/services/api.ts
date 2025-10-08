import axios from 'axios';
import {
  BalanceSheetData,
  CashFlowData,
  IncomeStatementData,
  AlphaVantageIncomeStatementResponse,
  AlphaVantageBalanceSheetResponse,
  AlphaVantageCashFlowResponse
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const financialApi = {
  getBalanceSheet: async (symbol: string, period: string = 'annual'): Promise<BalanceSheetData[]> => {
    const response = await apiClient.get(`/financial/balance-sheet/${symbol}?period=${period}`);
    return response.data;
  },

  getCashFlow: async (symbol: string, period: string = 'annual'): Promise<CashFlowData[]> => {
    const response = await apiClient.get(`/financial/cash-flow/${symbol}?period=${period}`);
    return response.data;
  },

  getIncomeStatement: async (symbol: string, period: string = 'annual'): Promise<IncomeStatementData[]> => {
    const response = await apiClient.get(`/financial/income-statement/${symbol}?period=${period}`);
    return response.data;
  },
};

export const alphaVantageApi = {
  getIncomeStatement: async (symbol: string): Promise<AlphaVantageIncomeStatementResponse> => {
    const response = await apiClient.get(`/alphavantage/income-statement/${symbol}`);
    return response.data;
  },

  getBalanceSheet: async (symbol: string): Promise<AlphaVantageBalanceSheetResponse> => {
    const response = await apiClient.get(`/alphavantage/balance-sheet/${symbol}`);
    return response.data;
  },

  getCashFlow: async (symbol: string): Promise<AlphaVantageCashFlowResponse> => {
    const response = await apiClient.get(`/alphavantage/cash-flow/${symbol}`);
    return response.data;
  },
};