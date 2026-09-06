<?php

use App\Http\Controllers\ProfileController;
use Illuminate\Foundation\Application;
use Illuminate\Support\Facades\Route;
use Inertia\Inertia;

Route::get('/', function () {
    return Inertia::render('Welcome', [
        'canLogin' => Route::has('login'),
        'canRegister' => Route::has('register'),
        'laravelVersion' => Application::VERSION,
        'phpVersion' => PHP_VERSION,
    ]);
});

Route::get('/dashboard', function () {
    return Inertia::render('Dashboard');
})->middleware(['auth', 'verified'])->name('dashboard');

Route::middleware('auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
    
    Route::post('/detect-emotion', function (Illuminate\Http\Request $request) {
        $request->validate(['sentence' => 'required|string|max:1000']);
        try {
            $response = Illuminate\Support\Facades\Http::timeout(5)->post('http://ai_api:8001/api/analyze', [
                'text' => $request->input('sentence')
            ]);
            $result = $response->successful() ? $response->json('data') : ['error' => 'AI Server Error'];
        } catch (\Exception $e) {
            $result = ['error' => 'Failed to connect to AI Microservice'];
        }
        return back()->with('result', $result)->with('sentence', $request->input('sentence'));
    })->name('detect.emotion');
});

require __DIR__.'/auth.php';
