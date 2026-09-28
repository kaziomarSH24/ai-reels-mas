<x-filament-panels::page>
    <div class="space-y-6">
        
        <div class="p-6 bg-white dark:bg-gray-900 rounded-lg shadow ring-1 ring-gray-950/5 dark:ring-white/10">
            <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Playlist URL</label>
                <input type="text" wire:model="playlist_url" placeholder="https://www.youtube.com/playlist?list=..." 
                    class="w-full rounded-lg border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white shadow-sm focus:border-primary-500 focus:ring-primary-500">
            </div>
            
            <x-filament::button wire:click="fetchLinks" wire:loading.attr="disabled">
                <span wire:loading.remove wire:target="fetchLinks">Fetch Links</span>
                <span wire:loading wire:target="fetchLinks">Fetching... Please wait...</span>
            </x-filament::button>
        </div>

        @if($extracted_links)
        <div class="p-6 bg-white dark:bg-gray-900 rounded-lg shadow ring-1 ring-gray-950/5 dark:ring-white/10 space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Extracted Links</label>
                <textarea wire:model="extracted_links" rows="10" id="links-textarea"
                    class="w-full rounded-lg border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white shadow-sm font-mono text-sm"></textarea>
            </div>

            <div class="flex gap-4">
                <button type="button" onclick="navigator.clipboard.writeText(document.getElementById('links-textarea').value).then(() => alert('Copied to clipboard!'))"
                    class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition text-sm font-semibold">
                    📋 Copy All
                </button>

                <x-filament::button wire:click="addToQueue" color="success">
                    🚀 Add All to Job Queue
                </x-filament::button>
            </div>
        </div>
        @endif

    </div>
</x-filament-panels::page>
