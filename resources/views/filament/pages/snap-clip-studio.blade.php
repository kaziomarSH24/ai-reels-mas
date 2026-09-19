<x-filament-panels::page>
    <div class="space-y-8">
        
        <!-- Video Input Section -->
        <div class="p-6 bg-white dark:bg-gray-900 rounded-xl shadow-sm ring-1 ring-gray-950/5 dark:ring-white/10">
            <h2 class="text-xl font-semibold tracking-tight text-gray-950 dark:text-white">Source Video</h2>
            <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Enter a YouTube URL to process the video and extract conversational highlights.</p>
            
            <form wire:submit="analyzeVideo" class="mt-5 flex flex-col sm:flex-row items-start sm:items-center gap-3">
                <input type="url" wire:model="youtubeUrl" placeholder="https://www.youtube.com/watch?v=..." class="w-full sm:flex-1 rounded-lg border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-4 py-2.5 shadow-sm focus:border-primary-500 focus:ring-primary-500 transition duration-75" required>
                
                <x-filament::button type="submit" size="lg" wire:loading.attr="disabled" class="w-full sm:w-auto shrink-0">
                    <span wire:loading.remove wire:target="analyzeVideo">Analyze Content</span>
                    <span wire:loading wire:target="analyzeVideo">Processing...</span>
                </x-filament::button>
            </form>
        </div>

        <!-- Curation Section -->
        @if(!empty($extractedClips))
        <div class="p-6 bg-white dark:bg-gray-900 rounded-xl shadow-sm ring-1 ring-gray-950/5 dark:ring-white/10">
            <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-4 mb-6">
                <div>
                    <h2 class="text-xl font-semibold tracking-tight text-gray-950 dark:text-white">Curate Clips</h2>
                    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Select the segments you wish to compile into the final reel.</p>
                </div>
                <div class="shrink-0">
                    <span class="inline-flex items-center rounded-md bg-primary-50 px-3 py-1.5 text-sm font-medium text-primary-700 ring-1 ring-inset ring-primary-700/10 dark:bg-primary-400/10 dark:text-primary-400 dark:ring-primary-400/30">
                        {{ count($selectedClipIds) }} Selected
                    </span>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                @foreach($extractedClips as $clip)
                    @php
                        $isSelected = in_array($clip['id'], $selectedClipIds);
                    @endphp
                    <div class="relative p-5 rounded-xl border transition-colors cursor-pointer {{ $isSelected ? 'border-primary-600 bg-primary-50 dark:border-primary-500 dark:bg-primary-500/10' : 'border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600' }}"
                         wire:click="toggleClipSelection({{ $clip['id'] }})">
                        
                        <div class="flex justify-between items-start gap-4 mb-3">
                            <h3 class="text-lg font-bold text-gray-900 dark:text-white leading-tight uppercase">{{ $clip['expression'] }}</h3>
                            <div class="shrink-0 pt-1">
                                @if($isSelected)
                                    <x-heroicon-s-check-circle class="w-6 h-6 text-primary-600 dark:text-primary-500"/>
                                @else
                                    <div class="w-6 h-6 rounded-full border-2 border-gray-300 dark:border-gray-600"></div>
                                @endif
                            </div>
                        </div>
                        
                        <div class="space-y-3">
                            <div>
                                <span class="inline-flex items-center rounded-md bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10 dark:bg-gray-400/10 dark:text-gray-400 dark:ring-gray-400/20 mb-2">
                                    {{ $clip['category'] ?? 'PHRASE' }}
                                </span>
                                <p class="text-sm text-gray-700 dark:text-gray-300">
                                    <span class="font-medium">Meaning:</span> {{ $clip['casual_meaning'] }}
                                </p>
                            </div>
                            
                            <div class="rounded-lg bg-gray-50 dark:bg-gray-800/50 p-3 text-sm">
                                <p class="italic text-gray-800 dark:text-gray-200">"{{ $clip['easy_example'] }}"</p>
                                <p class="text-gray-500 mt-1">{{ $clip['example_translation'] }}</p>
                            </div>
                        </div>
                        
                        <div class="mt-4 pt-3 border-t border-gray-100 dark:border-gray-700/50 flex justify-between items-center text-xs text-gray-500 dark:text-gray-400">
                            <span class="font-mono">{{ number_format((float)$clip['start_time'], 1) }}s - {{ number_format((float)$clip['end_time'], 1) }}s</span>
                            <span class="truncate ml-4" title="Whisper target">🎯 "{{ $clip['whisper_target'] }}"</span>
                        </div>
                    </div>
                @endforeach
            </div>

            <div class="mt-8 flex justify-end">
                <x-filament::button wire:click="generateReel" size="lg" color="primary" wire:loading.attr="disabled">
                    <span wire:loading.remove wire:target="generateReel">Generate Reel</span>
                    <span wire:loading wire:target="generateReel">Processing...</span>
                </x-filament::button>
            </div>
        </div>
        @endif

        <!-- Output Section -->
        @if($generatedReelUrl)
        <div class="p-6 bg-white dark:bg-gray-900 rounded-xl shadow-sm ring-1 ring-gray-950/5 dark:ring-white/10 border-t-4 border-t-success-500">
            <div class="text-center max-w-2xl mx-auto mb-6">
                <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Ready for Export</h2>
                <p class="text-sm text-gray-500 dark:text-gray-400">Your compilation reel has been successfully generated and is ready for download.</p>
            </div>

            <div class="flex justify-center mb-6">
                <div class="rounded-xl overflow-hidden shadow-lg ring-1 ring-gray-900/10">
                    <video controls autoplay class="w-full max-w-md bg-black" style="max-height: 600px;">
                        <source src="{{ $generatedReelUrl }}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
            </div>

            <div class="flex justify-center">
                <x-filament::button tag="a" href="{{ $generatedReelUrl }}" download="Reel_Export.mp4" color="success" size="lg" icon="heroicon-m-arrow-down-tray">
                    Download Video
                </x-filament::button>
            </div>
        </div>
        @endif

    </div>
</x-filament-panels::page>
