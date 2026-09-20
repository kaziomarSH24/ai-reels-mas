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
            $table->string('file_path')->nullable()->change();
        });
    }

    public function down(): void
    {
        Schema::table('generated_reels', function (Blueprint $table) {
            $table->string('file_path')->nullable(false)->change();
        });
    }
};
