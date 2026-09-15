<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // Drop old tables to start fresh with the new Master Plan architecture
        Schema::dropIfExists('movie_dialogues');
        Schema::dropIfExists('movies');

        Schema::create('movies', function (Blueprint $table) {
            $table->id();
            $table->string('title')->nullable();
            $table->string('youtube_url');
            $table->boolean('is_processed')->default(false);
            $table->string('thumbnail_url')->nullable();
            $table->timestamps();
        });

        Schema::create('movie_dialogues', function (Blueprint $table) {
            $table->id();
            $table->foreignId('movie_id')->constrained()->onDelete('cascade');
            $table->text('text'); // The actual spoken sentence
            $table->string('start_time'); // HH:MM:SS,mmm or seconds
            $table->string('end_time');
            $table->string('emotion')->nullable(); // DistilBERT result
            $table->text('translated_text')->nullable(); // BanglaT5 result
            $table->string('cefr_level')->nullable(); // Hard word level
            
            // Fulltext index for fast searching
            $table->fullText('text');
            $table->timestamps();
        });
        
        // A new table to track generated reels
        Schema::create('generated_reels', function (Blueprint $table) {
            $table->id();
            $table->foreignId('movie_id')->nullable()->constrained()->onDelete('set null');
            $table->string('target_word');
            $table->string('file_path'); // Local path or URL to the final MP4
            $table->boolean('is_posted_to_fb')->default(false);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('generated_reels');
        Schema::dropIfExists('movie_dialogues');
        Schema::dropIfExists('movies');
    }
};
