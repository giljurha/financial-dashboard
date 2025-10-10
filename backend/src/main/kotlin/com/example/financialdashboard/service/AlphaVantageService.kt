package com.example.financialdashboard.service

import com.example.financialdashboard.model.AlphaVantageBalanceSheetResponse
import com.example.financialdashboard.model.AlphaVantageCashFlowResponse
import com.example.financialdashboard.model.AlphaVantageIncomeStatementResponse
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.http.HttpStatus
import org.springframework.stereotype.Service
import org.springframework.web.reactive.function.client.WebClient
import org.springframework.web.reactive.function.client.WebClientResponseException
import reactor.core.publisher.Mono

@Service
class AlphaVantageService {

    private val logger = LoggerFactory.getLogger(AlphaVantageService::class.java)

    @Value("\${alphavantage-api.base-url}")
    private lateinit var baseUrl: String

    @Value("\${alphavantage-api.api-key}")
    private lateinit var apiKey: String

    private val webClient = WebClient.builder()
        .codecs { it.defaultCodecs().maxInMemorySize(16 * 1024 * 1024) }
        .build()

    /**
     * Get income statement data for a given symbol
     * @param symbol Stock symbol (e.g., "IBM")
     * @return Income statement data
     */
    fun getIncomeStatement(symbol: String): Mono<AlphaVantageIncomeStatementResponse> {
        val url = "$baseUrl?function=INCOME_STATEMENT&symbol=$symbol&apikey=$apiKey"
        logger.info("Fetching income statement for symbol: $symbol from URL: $url")

        return webClient.get()
            .uri(url)
            .retrieve()
            .onStatus({ status -> status.isError }) { response ->
                response.bodyToMono(String::class.java).flatMap { body ->
                    logger.error("AlphaVantage API HTTP error for income statement: status=${response.statusCode()}, body=$body")
                    Mono.error(WebClientResponseException.create(
                        response.statusCode().value(),
                        "AlphaVantage API HTTP error",
                        response.headers().asHttpHeaders(),
                        body.toByteArray(),
                        null
                    ))
                }
            }
            .bodyToMono(String::class.java)
            .flatMap { responseBody ->
                logger.debug("Raw response for income statement: $responseBody")

                try {
                    val objectMapper = com.fasterxml.jackson.module.kotlin.jacksonObjectMapper()
                    val response = objectMapper.readValue(responseBody, AlphaVantageIncomeStatementResponse::class.java)

                    // Check for error fields in the response
                    when {
                        response.errorMessage != null -> {
                            logger.error("AlphaVantage API error for income statement: ${response.errorMessage}")
                            Mono.error(RuntimeException("AlphaVantage API error: ${response.errorMessage}"))
                        }
                        response.information != null -> {
                            logger.error("AlphaVantage API information for income statement: ${response.information}")
                            Mono.error(RuntimeException("AlphaVantage API: ${response.information}"))
                        }
                        response.note != null -> {
                            logger.warn("AlphaVantage API note for income statement: ${response.note}")
                            Mono.error(RuntimeException("AlphaVantage API: ${response.note}"))
                        }
                        response.symbol == null || response.annualReports == null -> {
                            logger.error("AlphaVantage API returned incomplete data for income statement. Response: $responseBody")
                            Mono.error(RuntimeException("AlphaVantage API returned incomplete data"))
                        }
                        else -> Mono.just(response)
                    }
                } catch (e: Exception) {
                    logger.error("Failed to parse income statement response: ${e.message}. Response: $responseBody", e)
                    Mono.error(RuntimeException("Failed to parse AlphaVantage response: ${e.message}"))
                }
            }
            .doOnError { error ->
                logger.error("Error fetching income statement for $symbol: ${error.message}", error)
            }
            .onErrorResume { error ->
                logger.error("Failed to get income statement for $symbol: ${error.message}", error)
                Mono.error(RuntimeException("Failed to fetch income statement from AlphaVantage: ${error.message}", error))
            }
    }

    /**
     * Get balance sheet data for a given symbol
     * @param symbol Stock symbol (e.g., "IBM")
     * @return Balance sheet data
     */
    fun getBalanceSheet(symbol: String): Mono<AlphaVantageBalanceSheetResponse> {
        val url = "$baseUrl?function=BALANCE_SHEET&symbol=$symbol&apikey=$apiKey"
        logger.info("Fetching balance sheet for symbol: $symbol from URL: $url")

        return webClient.get()
            .uri(url)
            .retrieve()
            .onStatus({ status -> status.isError }) { response ->
                response.bodyToMono(String::class.java).flatMap { body ->
                    logger.error("AlphaVantage API HTTP error for balance sheet: status=${response.statusCode()}, body=$body")
                    Mono.error(WebClientResponseException.create(
                        response.statusCode().value(),
                        "AlphaVantage API HTTP error",
                        response.headers().asHttpHeaders(),
                        body.toByteArray(),
                        null
                    ))
                }
            }
            .bodyToMono(String::class.java)
            .flatMap { responseBody ->
                logger.debug("Raw response for balance sheet: $responseBody")

                try {
                    val objectMapper = com.fasterxml.jackson.module.kotlin.jacksonObjectMapper()
                    val response = objectMapper.readValue(responseBody, AlphaVantageBalanceSheetResponse::class.java)

                    // Check for error fields in the response
                    when {
                        response.errorMessage != null -> {
                            logger.error("AlphaVantage API error for balance sheet: ${response.errorMessage}")
                            Mono.error(RuntimeException("AlphaVantage API error: ${response.errorMessage}"))
                        }
                        response.information != null -> {
                            logger.error("AlphaVantage API information for balance sheet: ${response.information}")
                            Mono.error(RuntimeException("AlphaVantage API: ${response.information}"))
                        }
                        response.note != null -> {
                            logger.warn("AlphaVantage API note for balance sheet: ${response.note}")
                            Mono.error(RuntimeException("AlphaVantage API: ${response.note}"))
                        }
                        response.symbol == null || response.annualReports == null -> {
                            logger.error("AlphaVantage API returned incomplete data for balance sheet. Response: $responseBody")
                            Mono.error(RuntimeException("AlphaVantage API returned incomplete data"))
                        }
                        else -> Mono.just(response)
                    }
                } catch (e: Exception) {
                    logger.error("Failed to parse balance sheet response: ${e.message}. Response: $responseBody", e)
                    Mono.error(RuntimeException("Failed to parse AlphaVantage response: ${e.message}"))
                }
            }
            .doOnError { error ->
                logger.error("Error fetching balance sheet for $symbol: ${error.message}", error)
            }
            .onErrorResume { error ->
                logger.error("Failed to get balance sheet for $symbol: ${error.message}", error)
                Mono.error(RuntimeException("Failed to fetch balance sheet from AlphaVantage: ${error.message}", error))
            }
    }

    /**
     * Get cash flow statement data for a given symbol
     * @param symbol Stock symbol (e.g., "IBM")
     * @return Cash flow statement data
     */
    fun getCashFlowStatement(symbol: String): Mono<AlphaVantageCashFlowResponse> {
        val url = "$baseUrl?function=CASH_FLOW&symbol=$symbol&apikey=$apiKey"
        logger.info("Fetching cash flow statement for symbol: $symbol from URL: $url")

        return webClient.get()
            .uri(url)
            .retrieve()
            .onStatus({ status -> status.isError }) { response ->
                response.bodyToMono(String::class.java).flatMap { body ->
                    logger.error("AlphaVantage API HTTP error for cash flow: status=${response.statusCode()}, body=$body")
                    Mono.error(WebClientResponseException.create(
                        response.statusCode().value(),
                        "AlphaVantage API HTTP error",
                        response.headers().asHttpHeaders(),
                        body.toByteArray(),
                        null
                    ))
                }
            }
            .bodyToMono(String::class.java)
            .flatMap { responseBody ->
                logger.debug("Raw response for cash flow: $responseBody")

                try {
                    val objectMapper = com.fasterxml.jackson.module.kotlin.jacksonObjectMapper()
                    val response = objectMapper.readValue(responseBody, AlphaVantageCashFlowResponse::class.java)

                    // Check for error fields in the response
                    when {
                        response.errorMessage != null -> {
                            logger.error("AlphaVantage API error for cash flow: ${response.errorMessage}")
                            Mono.error(RuntimeException("AlphaVantage API error: ${response.errorMessage}"))
                        }
                        response.information != null -> {
                            logger.error("AlphaVantage API information for cash flow: ${response.information}")
                            Mono.error(RuntimeException("AlphaVantage API: ${response.information}"))
                        }
                        response.note != null -> {
                            logger.warn("AlphaVantage API note for cash flow: ${response.note}")
                            Mono.error(RuntimeException("AlphaVantage API: ${response.note}"))
                        }
                        response.symbol == null || response.annualReports == null -> {
                            logger.error("AlphaVantage API returned incomplete data for cash flow. Response: $responseBody")
                            Mono.error(RuntimeException("AlphaVantage API returned incomplete data"))
                        }
                        else -> Mono.just(response)
                    }
                } catch (e: Exception) {
                    logger.error("Failed to parse cash flow response: ${e.message}. Response: $responseBody", e)
                    Mono.error(RuntimeException("Failed to parse AlphaVantage response: ${e.message}"))
                }
            }
            .doOnError { error ->
                logger.error("Error fetching cash flow for $symbol: ${error.message}", error)
            }
            .onErrorResume { error ->
                logger.error("Failed to get cash flow for $symbol: ${error.message}", error)
                Mono.error(RuntimeException("Failed to fetch cash flow from AlphaVantage: ${error.message}", error))
            }
    }
}
