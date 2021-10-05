<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

/**
 * @method static findOrFail(int $id)
 */
class Todo extends Model
{
    use HasFactory;

    protected $fillable = ['title', 'is_done'];

}
