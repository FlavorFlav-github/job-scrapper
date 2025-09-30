FROM python:3.12-slim

WORKDIR /app

# Install system dependencies: chromium + cron + supervisor
RUN apt-get update && apt-get install -y \
    chromium chromium-driver cron supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Add cron job (every 6 hours run main.py)
RUN echo "0 */6 * * * root python /app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/scraper-cron \
    && chmod 0644 /etc/cron.d/scraper-cron \
    && crontab /etc/cron.d/scraper-cron

# Supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose Flask port
EXPOSE 5001

# Run Supervisor (manages cron + flask)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]