<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class GeneratedReel extends Model
{
    protected $fillable = [
        'video_id',
        'target_word',
        'file_path',
        'is_posted_to_fb',
    ];

    public function video()
    {
        return $this->belongsTo(Video::class);
    }
}
