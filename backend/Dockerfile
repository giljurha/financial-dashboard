# Multi-stage build for Spring Boot application
FROM gradle:8.4-jdk17 as builder

WORKDIR /app

# Copy gradle files first for better caching
COPY build.gradle.kts settings.gradle.kts ./
COPY gradle gradle

# Download dependencies
RUN gradle dependencies --no-daemon

# Copy source code
COPY src src

# Build the application
RUN gradle clean bootJar --no-daemon

# Runtime stage
FROM eclipse-temurin:17-jre-jammy

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy the built jar from builder stage
COPY --from=builder /app/build/libs/*.jar app.jar

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]