# Redis service for Render deployment
FROM redis:7-alpine

# Set to production mode
ENV REDIS_PORT=6379

# Enable persistence
RUN mkdir -p /data

# Copy custom Redis configuration (optional)
COPY redis.conf /usr/local/etc/redis/redis.conf

# Expose Redis port
EXPOSE 6379

# Run Redis with custom config
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
