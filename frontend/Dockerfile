# TuneScore Frontend Dockerfile
# Multi-stage build for optimized image size

FROM node:20-slim as builder

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install dependencies
RUN npm ci --quiet

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Production stage with nginx to serve static files
FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built static files from builder
COPY --from=builder /app/build /usr/share/nginx/html

# Create non-root user
RUN adduser -D -u 1000 tunescore && \
    chown -R tunescore:tunescore /usr/share/nginx/html && \
    chown -R tunescore:tunescore /var/cache/nginx && \
    chown -R tunescore:tunescore /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R tunescore:tunescore /var/run/nginx.pid

# Switch to non-root user
USER tunescore

# Expose port
EXPOSE 5128

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:5128/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

