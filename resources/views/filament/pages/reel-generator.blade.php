<x-filament-panels::page>
    <div class="space-y-6">
        
        <!-- Render the form -->
        <form wire:submit="generateReelAction" class="space-y-4">
            {{ $this->generatorForm }}

            <x-filament::button type="submit" color="primary" class="mt-4" wire:loading.attr="disabled">
                <span wire:loading.remove>Generate Reel</span>
                <span wire:loading>Processing FFmpeg (Wait 10-20s)...</span>
            </x-filament::button>
        </form>

        <!-- Display the generated video -->
        @if ($generatedReelUrl)
            <div class="mt-8 p-6 bg-white dark:bg-gray-800 rounded-xl shadow ring-1 ring-gray-900/5 dark:ring-white/10">
                <h3 class="text-xl font-bold mb-4 text-emerald-500">Your Reel is Ready! 🎉</h3>
                <p class="mb-4 text-sm text-gray-500">Video cropped to 9:16 vertical using AI FFmpeg engine.</p>
                
                <div class="flex justify-center">
                    <video controls style="max-height: 600px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                        <source src="{{ $generatedReelUrl }}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
                
                <div class="mt-6 flex justify-center">
                    <a href="{{ $generatedReelUrl }}" download class="px-4 py-2 bg-emerald-500 text-white rounded font-bold hover:bg-emerald-600">
                        Download Reel (MP4)
                    </a>
                </div>
            </div>
        @endif

    </div>
</x-filament-panels::page>
