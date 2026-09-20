<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class VideoJob extends Model
{
    use HasFactory;

    protected $fillable = [
        'youtube_url',
        'status',
        'retry_count',
        'error_log',
    ];
}
