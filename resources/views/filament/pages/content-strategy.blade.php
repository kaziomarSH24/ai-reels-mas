<x-filament-panels::page>
    <div class="space-y-6">
        <x-filament::card>
            <div class="prose max-w-none dark:prose-invert">
                <h2>Welcome to AI Content Strategy 🚀</h2>
                <p>
                    Not sure which word to make a video on today? Click the <strong>"Ask Gemini for Today's Best Reels"</strong> button at the top right. 
                    Gemini will analyze your entire database of movie vocabulary and suggest the top 5 most viral and trendy words to focus on!
                </p>
            </div>
        </x-filament::card>

        @if($isLoading)
            <x-filament::card>
                <div class="flex items-center justify-center p-8 space-x-4">
                    <x-filament::loading-indicator class="h-8 w-8 text-primary-500" />
                    <span class="text-lg font-medium">Gemini is analyzing your database... Please wait...</span>
                </div>
            </x-filament::card>
        @endif

        @if($aiRecommendation && !$isLoading)
            <x-filament::card>
                <div class="prose max-w-none dark:prose-invert p-4">
                    {!! \Illuminate\Support\Str::markdown($aiRecommendation) !!}
                </div>
            </x-filament::card>
        @endif
    </div>
</x-filament-panels::page>
