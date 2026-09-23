<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('video_jobs', function (Blueprint $table) {
            // We keep using 'youtube_url' column as a generic 'video_url' to avoid dropping data,
            // but we add 'source_type' to know how to process it.
            $table->string('source_type')->default('youtube')->after('youtube_url');
        });
    }

    public function down(): void
    {
        Schema::table('video_jobs', function (Blueprint $table) {
            $table->dropColumn('source_type');
        });
    }
};
