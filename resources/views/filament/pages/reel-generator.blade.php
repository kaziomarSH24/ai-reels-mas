<x-filament-panels::page>
    <div class="space-y-6">
        
        <!-- Render the form (Now it searches first) -->
        <form wire:submit="searchClipsAction" class="space-y-4">
            {{ $this->generatorForm }}

            <x-filament::button type="submit" color="primary" size="lg" icon="heroicon-m-magnifying-glass" class="mt-4" wire:loading.attr="disabled">
                <span wire:loading.remove wire:target="searchClipsAction">Search Database</span>
                <span wire:loading wire:target="searchClipsAction">Scanning...</span>
            </x-filament::button>
        </form>

        <!-- Preview Results -->
        @if ($hasSearched)
            <div class="mt-8 p-6 bg-white dark:bg-gray-900 rounded-xl shadow ring-1 ring-gray-900/5 dark:ring-white/10">
                <div class="mb-4">
                    <h3 class="text-xl font-bold">Analysis Results</h3>
                    <p style="color: gray; font-size: 0.9rem;">Found {{ count($searchResults) }} matching clips for your keyword.</p>
                </div>
                
                @if(empty($searchResults))
                    <p style="color: gray;">No dialogues found for this keyword in the database. Try another word.</p>
                @else
                    <div style="overflow-x: auto; margin-bottom: 20px;">
                        <table style="width: 100%; text-align: left; border-collapse: collapse;">
                            <thead>
                                <tr style="border-bottom: 1px solid #374151;">
                                    <th style="padding: 10px; font-weight: bold;">Timestamp</th>
                                    <th style="padding: 10px; font-weight: bold;">Target Word</th>
                                    <th style="padding: 10px; font-weight: bold;">Easy Example</th>
                                    <th style="padding: 10px; font-weight: bold;">Bengali Translation</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach($searchResults as $clip)
                                    <tr style="border-bottom: 1px solid #374151;">
                                        <td style="padding: 12px; color: gray; font-family: monospace;">{{ $clip['start_time'] }}</td>
                                        <td style="padding: 12px; font-weight: bold; color: #f59e0b;">{!! $clip['expression'] . ' <br><span style="color: #9ca3af; font-size: 0.85em;">(অর্থ: ' . $clip['casual_meaning'] . ')</span>' !!}</td>
                                        <td style="padding: 12px;">"{{ $clip['easy_example'] }}"</td>
                                        <td style="padding: 12px; color: #10b981;">{{ $clip['example_translation'] }}</td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Generate Button -->
                    <div style="display: flex; justify-content: flex-end; margin-top: 20px;">
                        <x-filament::button wire:click="generateReelAction" color="success" size="lg" icon="heroicon-m-film" wire:loading.attr="disabled">
                            <span wire:loading.remove wire:target="generateReelAction">Generate Compilation Reel</span>
                            <span wire:loading wire:target="generateReelAction">Processing FFmpeg Engine (Wait 10-20s)...</span>
                        </x-filament::button>
                    </div>
                @endif
            </div>
        @endif

        <!-- Display the generated video -->
        @if ($generatedReelUrl)
            <div class="mt-8 p-6 bg-white dark:bg-gray-800 rounded-xl shadow ring-1 ring-gray-900/5 dark:ring-white/10" style="border-top: 4px solid #10b981;">
                <h3 class="text-xl font-bold mb-2" style="color: #10b981;">Your Viral Reel is Ready! 🎉</h3>
                <p class="mb-4" style="color: gray; font-size: 0.9rem;">
                    The AI engine has successfully extracted, blurred, cropped, and highlighted the dictionary meanings.
                </p>
                
                <div style="display: flex; justify-content: center; margin-top: 20px;">
                    <video controls autoplay style="max-height: 500px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
                        <source src="{{ $generatedReelUrl }}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
                
                <div style="display: flex; justify-content: center; margin-top: 20px;">
                    <x-filament::button tag="a" href="{{ $generatedReelUrl }}" download="AI_Reel_{{ str_replace([' ', '.'], '_', $reelData['keyword'] ?? 'Compilation') }}.mp4" color="success" size="lg" icon="heroicon-m-arrow-down-tray">
                        Download MP4
                    </x-filament::button>
                </div>
            </div>
        @endif

    </div>
</x-filament-panels::page>
