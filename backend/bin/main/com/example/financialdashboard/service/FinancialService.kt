package com.example.financialdashboard.service

import com.example.financialdashboard.model.BalanceSheetResponse
import com.example.financialdashboard.model.CashFlowResponse
import com.example.financialdashboard.model.IncomeStatementResponse
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import org.springframework.web.reactive.function.client.WebClient
import reactor.core.publisher.Flux

@Service
class FinancialService {

    @Value("\${financial-api.base-url}")
    private lateinit var baseUrl: String

    @Value("\${financial-api.stable-base-url}")
    private lateinit var stableBaseUrl: String

    @Value("\${financial-api.api-key}")
    private lateinit var apiKey: String

    private val webClient = WebClient.builder().build()

    fun getBalanceSheet(symbol: String, period: String = "annual"): Flux<BalanceSheetResponse> {
        return webClient.get()
            .uri("$baseUrl/balance-sheet-statement/$symbol?period=$period&apikey=$apiKey")
            .retrieve()
            .bodyToFlux(BalanceSheetResponse::class.java)
    }

    fun getCashFlowStatement(symbol: String, period: String = "annual"): Flux<CashFlowResponse> {
        return webClient.get()
            .uri("$stableBaseUrl/cash-flow-statement?symbol=$symbol&period=$period&apikey=$apiKey")
            .retrieve()
            .bodyToFlux(CashFlowResponse::class.java)
    }

    fun getIncomeStatement(symbol: String, period: String = "annual"): Flux<IncomeStatementResponse> {
        return webClient.get()
            .uri("$stableBaseUrl/income-statement?symbol=$symbol&period=$period&apikey=$apiKey")
            .retrieve()
            .bodyToFlux(IncomeStatementResponse::class.java)
    }
}