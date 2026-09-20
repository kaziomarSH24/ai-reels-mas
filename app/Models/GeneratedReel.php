<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class GeneratedReel extends Model
{
    protected $fillable = [
        'video_id',
        'target_word',
        'status',
        'file_path',
        'error_log',
        'is_posted_to_fb',
    ];

    public function video()
    {
        return $this->belongsTo(Video::class);
    }
}
