<x-filament-panels::page>
    <div class="w-full">
        {{ $this->analyzerForm }}
    </div>

    <!-- Loading Animation (Shows immediately when the button is clicked) -->
    <div wire:loading wire:target="analyzeVideo" class="mt-8 w-full">
        <style>
            @keyframes custom-ping {
                75%, 100% { transform: scale(2); opacity: 0; }
            }
            @keyframes custom-pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: .5; }
            }
            @keyframes custom-spin {
                to { transform: rotate(360deg); }
            }
            .pulse-progress {
                animation: custom-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
            }
        </style>
        <div style="position: relative; padding: 2rem; background-color: rgba(17, 24, 39, 0.8); border-radius: 0.75rem; border: 1px solid rgba(16, 185, 129, 0.3); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1rem;">
            
            <!-- Dynamic Timer Component (Top Right Corner) -->
            <div x-data="{ seconds: 0 }"
                 x-init="setInterval(() => { if ($el.offsetWidth > 0) { seconds++; } else { seconds = 0; } }, 1000)"
                 style="position: absolute; top: 1.5rem; right: 1.5rem; background-color: rgba(0,0,0,0.5); padding: 0.5rem 1rem; border-radius: 0.5rem; border: 1px solid rgba(16, 185, 129, 0.3); color: #10b981; font-family: monospace; font-size: 1.25rem; font-weight: bold; display: flex; align-items: center; gap: 0.5rem;">
                <svg style="width: 1.25rem; height: 1.25rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span x-text="Math.floor(seconds / 60).toString().padStart(2, '0') + ':' + (seconds % 60).toString().padStart(2, '0')">00:00</span>
            </div>
            <div style="position: relative; width: 4rem; height: 4rem;">
                <!-- Outer pulsing ring -->
                <div style="position: absolute; inset: 0; border-radius: 9999px; border: 4px solid rgba(16, 185, 129, 0.3); animation: custom-ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
                <!-- Inner spinning ring -->
                <div style="position: absolute; inset: 0.5rem; border-radius: 9999px; border: 4px solid; border-color: #10b981 transparent #10b981 transparent; animation: custom-spin 1s linear infinite;"></div>
                <!-- Center dot -->
                <div style="position: absolute; inset: 1.5rem; border-radius: 9999px; background-color: #10b981; animation: custom-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;"></div>
            </div>
            <h3 style="font-size: 1.25rem; font-weight: 700; color: #fff; margin-top: 1rem;">AI Engine is Processing...</h3>
            <p style="color: #9ca3af; text-align: center; max-width: 28rem; font-size: 0.875rem;">
                Fetching YouTube subtitles, batch-translating with Gemini, and running CEFR filters. This will take <strong style="color: #10b981;">10-20 seconds</strong> depending on video length. Please wait...
            </p>
            <!-- Fake Progress Bar Animation -->
            <div style="width: 100%; max-width: 28rem; margin-top: 1.5rem; height: 0.5rem; background-color: rgba(31, 41, 55, 1); border-radius: 9999px; overflow: hidden;">
                <div class="pulse-progress" style="height: 100%; background-color: #10b981; border-radius: 9999px; width: 100%; opacity: 0.8;"></div>
            </div>
        </div>
    </div>

    <!-- Live Progress Bar Section -->
    @if($currentMovieId)
        <div class="mt-8 p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-white/10 shadow-sm w-full" wire:poll.2s>
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2" style="display: flex; align-items: center; gap: 8px;">
                    <svg style="width: 24px; height: 24px; color: #10b981;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                    AI Processing Status
                </h3>
                @if($isProcessing)
                    <span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 999px; background-color: rgba(16, 185, 129, 0.1); color: #10b981; font-size: 14px; font-weight: 500; border: 1px solid rgba(16, 185, 129, 0.2);">
                        <span style="width: 8px; height: 8px; border-radius: 50%; background-color: #10b981;" class="animate-pulse"></span>
                        Analyzing Live
                    </span>
                @else
                    <span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 999px; background-color: rgba(59, 130, 246, 0.1); color: #3b82f6; font-size: 14px; font-weight: 500; border: 1px solid rgba(59, 130, 246, 0.2);">
                        <svg style="width: 16px; height: 16px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                        Complete
                    </span>
                @endif
            </div>

            <!-- Progress Bar -->
            <div style="width: 100%; background-color: rgba(255,255,255,0.1); border-radius: 999px; height: 12px; margin-bottom: 8px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1);">
                <div style="background: linear-gradient(to right, #34d399, #14b8a6); height: 12px; border-radius: 999px; transition: all 0.5s ease-out; width: {{ $progressPercentage }}%;">
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-between; font-size: 14px; color: #9ca3af; font-weight: 500;">
                <span>{{ $processedDialogues }} / {{ $totalDialogues }} Dialogues Processed</span>
                <span>{{ $progressPercentage }}%</span>
            </div>
        </div>

        <!-- Live Filament Table -->
        <div class="mt-8">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Extracted Dialogues</h3>
            {{ $this->table }}
        </div>
    @endif
</x-filament-panels::page>
