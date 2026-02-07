# Production Nginx Dockerfile for Tirum
FROM nginx:stable-alpine

# Install curl for health checks
RUN apk add --no-cache curl bash

# Copy nginx configuration
COPY default.conf /etc/nginx/conf.d/default.conf

# Create directories for SSL and static files
RUN mkdir -p /etc/nginx/ssl /app/staticfiles /app/media

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health/ || exit 1

# Expose ports
EXPOSE 80 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
