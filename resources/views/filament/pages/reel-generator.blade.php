<x-filament-panels::page>
    <div class="space-y-6">
        
        <!-- Render the form (Now it searches first) -->
        <form wire:submit="searchClipsAction" class="space-y-4">
            {{ $this->generatorForm }}

            <x-filament::button type="submit" color="primary" class="mt-4" wire:loading.attr="disabled">
                <span wire:loading.remove wire:target="searchClipsAction">🔍 Search Clips</span>
                <span wire:loading wire:target="searchClipsAction">Searching Database...</span>
            </x-filament::button>
        </form>

        <!-- Preview Results -->
        @if ($hasSearched)
            <div class="mt-8 p-6 bg-white dark:bg-gray-800 rounded-xl shadow ring-1 ring-gray-900/5 dark:ring-white/10">
                <h3 class="text-xl font-bold mb-4 text-primary-500">Preview Dialogues</h3>
                
                @if(empty($searchResults))
                    <p class="text-gray-500">No dialogues found for this keyword in the database.</p>
                @else
                    <div class="overflow-x-auto mb-6">
                        <table class="w-full text-left border-collapse">
                            <thead>
                                <tr class="border-b dark:border-gray-700">
                                    <th class="py-2 px-4 font-semibold text-sm">Timestamp</th>
                                    <th class="py-2 px-4 font-semibold text-sm">Target Word</th>
                                    <th class="py-2 px-4 font-semibold text-sm">Original Dialogue</th>
                                    <th class="py-2 px-4 font-semibold text-sm">Bengali Translation</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach($searchResults as $clip)
                                    <tr class="border-b dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/25">
                                        <td class="py-3 px-4 text-sm text-gray-500">{{ $clip['start_time'] }}</td>
                                        <td class="py-3 px-4 text-sm font-bold text-amber-500">{{ $clip['target_word'] }}</td>
                                        <td class="py-3 px-4 text-sm">{{ $clip['text'] }}</td>
                                        <td class="py-3 px-4 text-sm text-emerald-500">{{ $clip['translated_text'] }}</td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Generate Button -->
                    <div class="flex justify-end">
                        <x-filament::button wire:click="generateReelAction" color="success" size="lg" wire:loading.attr="disabled">
                            <span wire:loading.remove wire:target="generateReelAction">🎬 Generate Compilation Reel</span>
                            <span wire:loading wire:target="generateReelAction">Processing FFmpeg & Gemini (Wait 30-40s)...</span>
                        </x-filament::button>
                    </div>
                @endif
            </div>
        @endif

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
