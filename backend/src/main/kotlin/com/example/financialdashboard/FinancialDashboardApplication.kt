package com.example.financialdashboard

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.boot.web.servlet.support.SpringBootServletInitializer

@SpringBootApplication
class FinancialDashboardApplication : SpringBootServletInitializer()

fun main(args: Array<String>) {
    runApplication<FinancialDashboardApplication>(*args)
}