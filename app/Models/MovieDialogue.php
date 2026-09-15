<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class MovieDialogue extends Model
{
    protected $fillable = [
        'movie_id',
        'start_time',
        'end_time',
        'dialogue_text',
        'emotion',
        'cefr_level',
    ];

    public function movie()
    {
        return $this->belongsTo(Movie::class);
    }
}
