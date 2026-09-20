<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ScrapedClip extends Model
{
    protected $fillable = [
        'target_word',
        'file_path',
        'source',
        'is_used',
    ];
}
