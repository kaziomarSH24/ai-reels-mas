<x-filament-panels::page>
    <div class="space-y-8">
        
        <!-- Search Section -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-2">🎬 Reel Generator Studio</h2>
            <p class="text-gray-500 dark:text-gray-400 mb-6 text-sm">Type a keyword below to scan the AI database for the most viral movie dialogues.</p>
            
            <form wire:submit="searchClipsAction" class="space-y-4">
                {{ $this->generatorForm }}

                <div class="flex items-center space-x-4 mt-4">
                    <x-filament::button type="submit" size="lg" color="primary" wire:loading.attr="disabled">
                        <span wire:loading.remove wire:target="searchClipsAction">
                            <x-heroicon-o-magnifying-glass class="w-5 h-5 inline-block mr-1"/> Search Database
                        </span>
                        <span wire:loading wire:target="searchClipsAction">
                            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                            Scanning...
                        </span>
                    </x-filament::button>
                </div>
            </form>
        </div>

        <!-- Preview Results Section -->
        @if ($hasSearched)
            <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
                <div class="p-6 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center bg-gray-50 dark:bg-gray-800/50">
                    <div>
                        <h3 class="text-lg font-bold text-gray-800 dark:text-white">Analysis Results</h3>
                        <p class="text-sm text-gray-500 mt-1">Found {{ count($searchResults) }} matching clips for your keyword.</p>
                    </div>
                    @if(count($searchResults) > 0)
                        <span class="px-3 py-1 bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 rounded-full text-xs font-bold border border-emerald-200 dark:border-emerald-800">
                            Ready to Generate
                        </span>
                    @endif
                </div>
                
                <div class="p-0">
                    @if(empty($searchResults))
                        <div class="p-12 text-center">
                            <x-heroicon-o-face-frown class="w-12 h-12 mx-auto text-gray-400 mb-4"/>
                            <h3 class="text-lg font-medium text-gray-900 dark:text-white">No dialogues found</h3>
                            <p class="text-gray-500 mt-1">Try searching for a different keyword like "destiny" or "love".</p>
                        </div>
                    @else
                        <div class="overflow-x-auto">
                            <table class="w-full text-left border-collapse">
                                <thead class="bg-gray-50 dark:bg-gray-800/50">
                                    <tr>
                                        <th class="py-4 px-6 font-semibold text-xs text-gray-500 uppercase tracking-wider">Timestamp</th>
                                        <th class="py-4 px-6 font-semibold text-xs text-gray-500 uppercase tracking-wider">AI Target Word</th>
                                        <th class="py-4 px-6 font-semibold text-xs text-gray-500 uppercase tracking-wider">Original Dialogue</th>
                                        <th class="py-4 px-6 font-semibold text-xs text-gray-500 uppercase tracking-wider">Bengali Translation</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
                                    @foreach($searchResults as $clip)
                                        <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors">
                                            <td class="py-4 px-6 text-sm">
                                                <span class="font-mono bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-gray-600 dark:text-gray-400 text-xs border border-gray-200 dark:border-gray-700">
                                                    {{ $clip['start_time'] }}
                                                </span>
                                            </td>
                                            <td class="py-4 px-6">
                                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-400 border border-amber-200 dark:border-amber-800">
                                                    {{ $clip['target_word'] }}
                                                </span>
                                            </td>
                                            <td class="py-4 px-6 text-sm text-gray-700 dark:text-gray-300 font-medium">
                                                "{{ $clip['text'] }}"
                                            </td>
                                            <td class="py-4 px-6 text-sm text-emerald-600 dark:text-emerald-400">
                                                {{ $clip['translated_text'] }}
                                            </td>
                                        </tr>
                                    @endforeach
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- Generate Button -->
                        <div class="p-6 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-800 flex justify-end">
                            <x-filament::button wire:click="generateReelAction" color="success" size="lg" wire:loading.attr="disabled" class="shadow-lg hover:shadow-xl transition-all">
                                <span wire:loading.remove wire:target="generateReelAction">
                                    <x-heroicon-o-film class="w-5 h-5 inline-block mr-2"/> Generate Compilation Reel
                                </span>
                                <span wire:loading wire:target="generateReelAction">
                                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                                    Processing Engine (Wait 30s)...
                                </span>
                            </x-filament::button>
                        </div>
                    @endif
                </div>
            </div>
        @endif

        <!-- Display the generated video -->
        @if ($generatedReelUrl)
            <div class="bg-gradient-to-r from-emerald-500 to-teal-600 rounded-2xl shadow-xl overflow-hidden text-white relative">
                <!-- Decorative background elements -->
                <div class="absolute top-0 right-0 -mt-16 -mr-16 text-white opacity-10">
                    <x-heroicon-s-sparkles class="w-64 h-64"/>
                </div>
                
                <div class="p-8 relative z-10 flex flex-col items-center">
                    <h3 class="text-3xl font-extrabold mb-2 text-center tracking-tight">Your Viral Reel is Ready! 🚀</h3>
                    <p class="mb-8 text-emerald-100 text-center max-w-lg">
                        The AI engine has successfully extracted, blurred, cropped, and highlighted the dictionary meanings for your clips.
                    </p>
                    
                    <div class="bg-black/20 p-2 rounded-2xl backdrop-blur-sm border border-white/10 shadow-2xl">
                        <video controls class="rounded-xl max-h-[500px] shadow-inner" autoplay>
                            <source src="{{ $generatedReelUrl }}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>
                    </div>
                    
                    <div class="mt-8 flex justify-center space-x-4">
                        <a href="{{ $generatedReelUrl }}" download class="px-6 py-3 bg-white text-emerald-600 rounded-lg font-bold shadow-lg hover:bg-emerald-50 hover:-translate-y-0.5 transition-all flex items-center">
                            <x-heroicon-o-arrow-down-tray class="w-5 h-5 mr-2"/> Download MP4
                        </a>
                    </div>
                </div>
            </div>
        @endif

    </div>
</x-filament-panels::page>
