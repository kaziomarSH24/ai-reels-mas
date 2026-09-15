<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class MovieDialogue extends Model
{
    protected $guarded = [];

    public function movie()
    {
        return $this->belongsTo(Movie::class);
    }
}
