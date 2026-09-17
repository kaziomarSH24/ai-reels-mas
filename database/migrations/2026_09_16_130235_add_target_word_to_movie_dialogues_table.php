<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('movie_dialogues', function (Blueprint $table) {
            $table->string('target_word')->nullable()->after('text');
        });
    }

    public function down(): void
    {
        Schema::table('movie_dialogues', function (Blueprint $table) {
            $table->dropColumn('target_word');
        });
    }
};
