<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class GeneratedReel extends Model
{
    protected $fillable = [
        'target_word',
        'file_path',
        'is_posted_to_fb',
    ];
}
