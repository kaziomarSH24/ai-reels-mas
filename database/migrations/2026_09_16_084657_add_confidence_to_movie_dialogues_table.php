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
        Schema::table('movie_dialogues', function (Blueprint $table) {
            $table->decimal('emotion_confidence', 5, 2)->nullable();
            $table->decimal('cefr_confidence', 5, 2)->nullable();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('movie_dialogues', function (Blueprint $table) {
            $table->dropColumn(['emotion_confidence', 'cefr_confidence']);
        });
    }
};
