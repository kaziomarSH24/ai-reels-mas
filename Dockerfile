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
    python3-venv

# Clear cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd

# Install Python packages for Video Processing, Subtitles & AI Translation
# We use --break-system-packages because in Docker it's safe to install globally
RUN pip3 install --break-system-packages moviepy Pillow pysrt requests scikit-learn pandas torch transformers sentencepiece protobuf

# Get latest Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /var/www

# Expose port 9000 and start php-fpm server
EXPOSE 9000
CMD ["php-fpm"]
