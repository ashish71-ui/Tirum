FROM nginx:stable-alpine

RUN apk add --no-cache curl bash

# Copy Nginx config
COPY default.conf /etc/nginx/conf.d/default.conf

# Create static/media dirs
RUN mkdir -p /app/staticfiles /app/media /etc/nginx/ssl

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health/ || exit 1

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
