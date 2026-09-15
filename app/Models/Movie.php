<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Movie extends Model
{
    protected $fillable = [
        'title',
        'genre',
        'imdb_rating',
        'source_url',
        'video_url',
        'subtitle_url',
        'is_processed',
    ];

    public function dialogues()
    {
        return $this->hasMany(MovieDialogue::class);
    }
}
