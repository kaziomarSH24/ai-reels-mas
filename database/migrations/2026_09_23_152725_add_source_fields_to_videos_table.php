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
        Schema::table('videos', function (Blueprint $table) {
            // Make youtube_url nullable (now supports all source types)
            $table->string('youtube_url')->nullable()->change();
            // Direct source URL: Google Drive, R2, or any direct link
            $table->string('source_url')->nullable()->after('youtube_url');
            // Source type: youtube, gdrive, direct
            $table->string('source_type')->default('youtube')->after('source_url');
            // Uploaded SRT subtitle file path
            $table->string('subtitle_path')->nullable()->after('source_type');
            // Total dialogues indexed from SRT
            $table->integer('dialogue_count')->default(0)->after('subtitle_path');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('videos', function (Blueprint $table) {
            $table->dropColumn(['source_url', 'source_type', 'subtitle_path', 'dialogue_count']);
            $table->string('youtube_url')->nullable(false)->change();
        });
    }
};
