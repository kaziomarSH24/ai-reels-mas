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
        Schema::table('generated_reels', function (Blueprint $table) {
            $table->enum('status', ['pending', 'processing', 'completed', 'failed'])->default('pending')->after('target_word');
            $table->text('error_log')->nullable()->after('file_path');
        });
    }

    public function down(): void
    {
        Schema::table('generated_reels', function (Blueprint $table) {
            $table->dropColumn(['status', 'error_log']);
        });
    }
};
