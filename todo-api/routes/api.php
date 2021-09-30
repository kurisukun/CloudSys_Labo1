<?php

use App\Http\Controllers\ApiController;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| is assigned the "api" middleware group. Enjoy building your API!
|
*/

Route::prefix('v1')->group(function () {
    Route::get('/', [ApiController::class, 'index']);
    Route::post('/', [ApiController::class, 'add']);
    Route::delete('/{id}', [ApiController::class, 'remove'])->whereNumber('id');
    Route::put('/toggle/{id}', [ApiController::class, 'toggle'])->whereNumber('id');
});
