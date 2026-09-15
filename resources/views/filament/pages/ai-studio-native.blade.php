<x-filament-panels::page>
    <div class="w-full">
        {{ $this->analyzerForm }}
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
