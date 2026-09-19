<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Video extends Model
{
    protected $guarded = [];

    public function clips()
    {
        return $this->hasMany(VideoClip::class);
    }
}
