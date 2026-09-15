<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('movie_dialogues', function (Blueprint $table) {
            $table->id();
            $table->foreignId('movie_id')->constrained()->cascadeOnDelete();
            $table->string('start_time'); // Format: HH:MM:SS,mmm
            $table->string('end_time');   // Format: HH:MM:SS,mmm
            $table->text('dialogue_text');
            $table->string('emotion')->nullable();
            $table->string('cefr_level')->nullable();
            $table->timestamps();

            // FullText search index for fast dialogue lookup
            $table->fullText('dialogue_text');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('movie_dialogues');
    }
};
