<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // Drop old tables to start fresh with the new Master Plan architecture
        Schema::dropIfExists('generated_reels');
        Schema::dropIfExists('video_clips');
        Schema::dropIfExists('videos');
        
        // Also drop legacy tables if they exist
        Schema::dropIfExists('movie_dialogues');
        Schema::dropIfExists('movies');
        Schema::dropIfExists('analysis_histories');

        Schema::create('videos', function (Blueprint $table) {
            $table->id();
            $table->string('title')->nullable();
            $table->string('youtube_url');
            $table->boolean('is_processed')->default(false);
            $table->string('thumbnail_url')->nullable();
            $table->timestamps();
        });

        Schema::create('video_clips', function (Blueprint $table) {
            $table->id();
            $table->foreignId('video_id')->constrained()->onDelete('cascade');
            
            // Core Extraction Fields (Based on new Gemini Schema)
            $table->string('expression');                 // "I'm broke" (UI Display)
            $table->string('whisper_target')->nullable(); // "I'm completely broke" (Hidden, for exact video crop)
            $table->string('category')->nullable();       // IDIOM, ADVANCED_WORD, DAILY_PHRASE
            $table->string('casual_meaning')->nullable(); // "পকেট ফাঁকা"
            
            // Sentence Context
            $table->text('original_sentence');            // The full sentence spoken
            $table->text('original_translation')->nullable(); // Bengali translation of full sentence
            
            // Easy Learning Example
            $table->text('easy_example')->nullable();     // "I can't buy that shirt, I'm broke."
            $table->text('example_translation')->nullable(); // "আমি ওই শার্টটা কিনতে পারবো না..."
            
            // Timestamps
            $table->string('start_time');                 // rough_start
            $table->string('end_time');                   // rough_end
            
            // Fulltext index for fast searching in dashboard
            $table->fullText('original_sentence');
            $table->timestamps();
        });
        
        // A new table to track generated reels
        Schema::create('generated_reels', function (Blueprint $table) {
            $table->id();
            $table->foreignId('video_id')->nullable()->constrained()->onDelete('set null');
            $table->string('target_word');
            $table->string('file_path'); // Local path or URL to the final MP4
            $table->boolean('is_posted_to_fb')->default(false);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('generated_reels');
        Schema::dropIfExists('video_clips');
        Schema::dropIfExists('videos');
    }
};
