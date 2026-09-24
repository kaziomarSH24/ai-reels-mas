FROM php:8.4-fpm

# Install system dependencies for PHP, Python, and FFmpeg
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip \
    ffmpeg \
    python3 \
    python3-pip \
    python3-venv \
    libicu-dev \
    libzip-dev \
    netcat-traditional \
    chromium \
    chromium-driver \
    xvfb \
    nodejs

# Clear cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd intl zip

# Install Redis extension
RUN pecl install redis && docker-php-ext-enable redis

# Install Python packages for Video Processing, Subtitles & AI Translation
# We use CPU-only PyTorch to avoid massive 3GB NVIDIA CUDA downloads in Docker
RUN pip3 install --break-system-packages torch --index-url https://download.pytorch.org/whl/cpu
RUN pip3 install --break-system-packages moviepy Pillow pysrt requests scikit-learn pandas transformers sentencepiece protobuf fastapi uvicorn pydantic yt-dlp google-generativeai openai-whisper youtube-transcript-api numpy webvtt-py selenium undetected-chromedriver pyvirtualdisplay webdriver-manager

# Get latest Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /var/www

# Copy source code
COPY . /var/www

# Create required Laravel cache directories (since they are dockerignored)
RUN mkdir -p /var/www/storage/framework/sessions \
    /var/www/storage/framework/views \
    /var/www/storage/framework/cache \
    /var/www/bootstrap/cache

# Install PHP dependencies
RUN composer install --no-dev --optimize-autoloader

# Set permissions for Laravel
RUN chown -R www-data:www-data /var/www/storage /var/www/bootstrap/cache

# Copy the entrypoint script
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose port 9000
EXPOSE 9000

ENTRYPOINT ["entrypoint.sh"]
CMD ["php-fpm"]
