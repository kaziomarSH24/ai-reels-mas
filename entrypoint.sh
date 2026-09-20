#!/bin/sh
set -e

# --- Database Wait Logic ---
DB_HOST_CHECK=${DB_HOST:-ai_reels_db}
DB_PORT_CHECK=${DB_PORT:-3306}

echo "Attempting to connect to database at: ${DB_HOST_CHECK}:${DB_PORT_CHECK}"

# Loop until the database container is ready to accept connections
while ! nc -z ${DB_HOST_CHECK} ${DB_PORT_CHECK}; do
  echo "Waiting for database connection..."
  sleep 2
done
echo "Database connected successfully!"

# --- Set Permissions ---
echo "Setting storage and cache permissions..."
chown -R www-data:www-data /var/www/storage /var/www/bootstrap/cache || true
chmod -R 775 /var/www/storage /var/www/bootstrap/cache || true

# --- Laravel Optimization & Queue Preparation ---
echo "Clearing old Laravel caches..."
php artisan config:clear || true
php artisan route:clear || true
php artisan view:clear || true

if [ "$APP_ENV" = "production" ]; then
    echo "PRODUCTION MODE: Running optimizations..."
    php artisan config:cache
    php artisan route:cache
    php artisan view:cache
    
    # Run migrations automatically
    echo "Running database migrations..."
    php artisan migrate --force
else
    echo "DEVELOPMENT MODE: Running migrations..."
    # Always run migrations to make sure tables (like jobs) exist
    php artisan migrate --force || true
fi

# --- Role-Based Execution ---
role=${1}
if [ "$role" = "queue" ]; then
    echo "Running the queue worker / Horizon..."
    shift
    exec php artisan "$@"
elif [ "$role" = "scheduler" ]; then
    echo "Running the scheduler..."
    shift
    exec "$@"
elif [ "$role" = "api" ]; then
    echo "Running the Python API..."
    shift
    cd /var/www/python_engine
    exec uvicorn main:app --host 0.0.0.0 --port 8001 --reload
else
    echo "Starting PHP-FPM..."
    exec php-fpm
fi
