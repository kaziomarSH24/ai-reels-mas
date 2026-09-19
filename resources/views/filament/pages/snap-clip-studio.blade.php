<x-filament-panels::page>
    <style>
        .clip-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; margin-top: 1rem; }
        .clip-card { cursor: pointer; border-radius: 0.75rem; border: 2px solid #e5e7eb; background-color: #ffffff; padding: 1.25rem; transition: all 0.2s; }
        .clip-card.selected { border-color: #10b981; background-color: rgba(16, 185, 129, 0.05); }
        .clip-title { font-size: 1.125rem; font-weight: 700; text-transform: uppercase; color: #111827; margin: 0; }
        .clip-meaning { font-size: 0.875rem; margin-bottom: 1rem; color: #374151; }
        .clip-example-box { background-color: #f3f4f6; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 1rem; }
        .clip-example-text { font-style: italic; font-size: 0.875rem; color: #111827; margin: 0; font-weight: 500; }
        .clip-example-trans { font-size: 0.75rem; color: #4b5563; margin-top: 0.25rem; }
        .clip-meta { border-top: 1px solid #e5e7eb; padding-top: 0.75rem; display: flex; justify-content: space-between; font-size: 0.75rem; color: #6b7280; }
        
        /* Dark Mode */
        .dark .clip-card { border-color: #374151; background-color: #1f2937; }
        .dark .clip-card.selected { border-color: #10b981; background-color: rgba(16, 185, 129, 0.1); }
        .dark .clip-title { color: #f9fafb; }
        .dark .clip-meaning { color: #d1d5db; }
        .dark .clip-example-box { background-color: #374151; }
        .dark .clip-example-text { color: #f3f4f6; }
        .dark .clip-example-trans { color: #9ca3af; }
        .dark .clip-meta { border-top-color: #4b5563; color: #9ca3af; }
    </style>

    <!-- Video Input Section -->
    <x-filament::section
        icon="heroicon-o-video-camera"
        icon-color="primary"
    >
        <x-slot name="heading">
            Source Video
        </x-slot>
        <x-slot name="description">
            Enter a YouTube URL to process the video and extract conversational highlights.
        </x-slot>

        <form wire:submit="analyzeVideo" style="display: flex; gap: 1rem; align-items: center; margin-top: 1rem;">
            <div style="flex: 1;">
                <x-filament::input.wrapper>
                    <x-filament::input
                        type="url"
                        wire:model="youtubeUrl"
                        placeholder="https://www.youtube.com/watch?v=..."
                        required
                    />
                </x-filament::input.wrapper>
            </div>
            
            <x-filament::button type="submit" size="lg" wire:loading.attr="disabled">
                <span wire:loading.remove wire:target="analyzeVideo">Analyze Content</span>
                <span wire:loading wire:target="analyzeVideo">Processing...</span>
            </x-filament::button>
        </form>
    </x-filament::section>

    <!-- Curation Section -->
    @if(!empty($extractedClips))
    <x-filament::section
        icon="heroicon-o-squares-2x2"
        icon-color="success"
    >
        <x-slot name="heading">
            Curate Clips ({{ count($selectedClipIds) }} Selected)
        </x-slot>
        <x-slot name="description">
            Select the segments you wish to compile into the final reel.
        </x-slot>

        <div class="clip-grid">
            @foreach($extractedClips as $clip)
                @php
                    $isSelected = in_array($clip['id'], $selectedClipIds);
                @endphp
                
                <div 
                    wire:click="toggleClipSelection({{ $clip['id'] }})"
                    class="clip-card {{ $isSelected ? 'selected' : '' }}"
                >
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                        <h3 class="clip-title">
                            {{ $clip['expression'] }}
                        </h3>
                        <div>
                            @if($isSelected)
                                <x-heroicon-s-check-circle style="width: 1.5rem; height: 1.5rem; color: #10b981;"/>
                            @else
                                <div style="width: 1.5rem; height: 1.5rem; border-radius: 9999px; border: 2px solid #9ca3af;"></div>
                            @endif
                        </div>
                    </div>

                    <x-filament::badge color="info" style="margin-bottom: 0.75rem; display: inline-block;">
                        {{ $clip['category'] ?? 'PHRASE' }}
                    </x-filament::badge>

                    <p class="clip-meaning">
                        <strong>Meaning:</strong> {{ $clip['casual_meaning'] }}
                    </p>

                    <div class="clip-example-box">
                        <p class="clip-example-text">"{{ $clip['easy_example'] }}"</p>
                        <p class="clip-example-trans">{{ $clip['example_translation'] }}</p>
                    </div>

                    <div class="clip-meta">
                        <span style="font-family: monospace;">{{ number_format((float)$clip['start_time'], 1) }}s - {{ number_format((float)$clip['end_time'], 1) }}s</span>
                        <span>🎯 "{{ $clip['whisper_target'] }}"</span>
                    </div>
                </div>
            @endforeach
        </div>

        <div style="margin-top: 2rem; display: flex; justify-content: flex-end;">
            <x-filament::button wire:click="generateReel" size="lg" color="success" wire:loading.attr="disabled">
                <span wire:loading.remove wire:target="generateReel">Generate Reel</span>
                <span wire:loading wire:target="generateReel">Processing...</span>
            </x-filament::button>
        </div>
    </x-filament::section>
    @endif

    <!-- Output Section -->
    @if($generatedReelUrl)
    <x-filament::section
        icon="heroicon-o-film"
        icon-color="success"
    >
        <x-slot name="heading">
            Ready for Export
        </x-slot>
        <x-slot name="description">
            Your compilation reel has been successfully generated and is ready for download.
        </x-slot>

        <div style="display: flex; flex-direction: column; align-items: center; gap: 1.5rem; margin-top: 1rem;">
            <video controls autoplay style="max-height: 500px; border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <source src="{{ $generatedReelUrl }}" type="video/mp4">
                Your browser does not support the video tag.
            </video>

            <x-filament::button tag="a" href="{{ $generatedReelUrl }}" download="Reel_Export.mp4" color="success" size="lg" icon="heroicon-m-arrow-down-tray">
                Download Video
            </x-filament::button>
        </div>
    </x-filament::section>
    @endif
</x-filament-panels::page>