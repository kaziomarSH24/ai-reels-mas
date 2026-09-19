<x-filament-panels::page>
    <div class="space-y-8">
        
        <!-- STEP 1: Input URL -->
        <div class="p-6 bg-white dark:bg-gray-900 rounded-xl shadow ring-1 ring-gray-900/5 dark:ring-white/10">
            <h2 class="text-2xl font-bold mb-4" style="color: #f59e0b;">Step 1: Extract Premium Vocabulary</h2>
            <p class="mb-4 text-gray-500 text-sm">Paste a YouTube Video URL (e.g., podcast, interview) to automatically extract highly conversational phrases, idioms, and advanced vocabulary using Gemini AI.</p>
            
            <form wire:submit="analyzeVideo" class="flex items-center gap-4">
                <input type="text" wire:model="youtubeUrl" placeholder="https://www.youtube.com/watch?v=..." class="flex-1 rounded-lg border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-4 py-3 shadow-sm focus:border-primary-500 focus:ring-primary-500" required>
                
                <x-filament::button type="submit" size="lg" icon="heroicon-m-sparkles" wire:loading.attr="disabled" color="primary">
                    <span wire:loading.remove wire:target="analyzeVideo">Analyze Video</span>
                    <span wire:loading wire:target="analyzeVideo">AI is reading subtitles...</span>
                </x-filament::button>
            </form>
        </div>

        <!-- STEP 2: Curate & Select -->
        @if(!empty($extractedClips))
        <div class="p-6 bg-white dark:bg-gray-900 rounded-xl shadow ring-1 ring-gray-900/5 dark:ring-white/10" style="border-top: 4px solid #3b82f6;">
            <div class="flex justify-between items-center mb-6">
                <div>
                    <h2 class="text-2xl font-bold" style="color: #3b82f6;">Step 2: Curate Your Reel</h2>
                    <p class="text-gray-500 text-sm">Select the exact phrases you want to include in your viral reel.</p>
                </div>
                <div>
                    <span class="px-4 py-2 bg-blue-100 text-blue-800 rounded-full font-bold">
                        {{ count($selectedClipIds) }} Selected
                    </span>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                @foreach($extractedClips as $clip)
                    @php
                        $isSelected = in_array($clip['id'], $selectedClipIds);
                    @endphp
                    <div class="p-5 rounded-xl border-2 transition-all cursor-pointer {{ $isSelected ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-200 dark:border-gray-700 hover:border-gray-400' }}"
                         wire:click="toggleClipSelection({{ $clip['id'] }})">
                        
                        <div class="flex justify-between items-start mb-2">
                            <h3 class="text-xl font-black uppercase text-gray-900 dark:text-white">{{ $clip['expression'] }}</h3>
                            @if($isSelected)
                                <x-heroicon-s-check-circle class="w-6 h-6 text-blue-500"/>
                            @else
                                <div class="w-6 h-6 rounded-full border-2 border-gray-300"></div>
                            @endif
                        </div>
                        
                        <span class="inline-block px-2 py-1 bg-gray-200 dark:bg-gray-700 text-xs rounded mb-3 font-semibold text-gray-700 dark:text-gray-300">
                            {{ $clip['category'] ?? 'PHRASE' }}
                        </span>

                        <p class="text-sm text-gray-600 dark:text-gray-300 mb-2">
                            <strong class="text-green-600 dark:text-green-400">Meaning:</strong> {{ $clip['casual_meaning'] }}
                        </p>
                        
                        <div class="p-3 bg-gray-100 dark:bg-gray-800 rounded mt-3">
                            <p class="text-xs italic text-gray-800 dark:text-gray-200">"{{ $clip['easy_example'] }}"</p>
                            <p class="text-xs text-gray-500 mt-1">{{ $clip['example_translation'] }}</p>
                        </div>
                        
                        <div class="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700 flex justify-between text-xs text-gray-400 font-mono">
                            <span>{{ number_format((float)$clip['start_time'], 1) }}s - {{ number_format((float)$clip['end_time'], 1) }}s</span>
                            <span title="Exact speech whisper will search for">🎯 "{{ $clip['whisper_target'] }}"</span>
                        </div>
                    </div>
                @endforeach
            </div>

            <div class="mt-8 flex justify-end">
                <x-filament::button wire:click="generateReel" size="xl" color="success" icon="heroicon-m-film" wire:loading.attr="disabled">
                    <span wire:loading.remove wire:target="generateReel">Create Viral Reel</span>
                    <span wire:loading wire:target="generateReel">Rendering video (This takes time)...</span>
                </x-filament::button>
            </div>
        </div>
        @endif

        <!-- STEP 3: Output Video -->
        @if($generatedReelUrl)
        <div class="p-6 bg-white dark:bg-gray-900 rounded-xl shadow ring-1 ring-gray-900/5 dark:ring-white/10" style="border-top: 4px solid #10b981;">
            <div class="text-center mb-6">
                <h2 class="text-3xl font-black text-green-500 mb-2">🎉 Reel is Ready!</h2>
                <p class="text-gray-500">Your compilation reel has been cropped, synced, and watermarked successfully.</p>
            </div>

            <div class="flex justify-center mb-6">
                <video controls autoplay class="rounded-xl shadow-2xl" style="max-height: 600px; border: 1px solid #374151;">
                    <source src="{{ $generatedReelUrl }}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>

            <div class="flex justify-center gap-4">
                <x-filament::button tag="a" href="{{ $generatedReelUrl }}" download="AI_Reel.mp4" color="success" size="lg" icon="heroicon-m-arrow-down-tray">
                    Download MP4
                </x-filament::button>
            </div>
        </div>
        @endif

    </div>
</x-filament-panels::page>
