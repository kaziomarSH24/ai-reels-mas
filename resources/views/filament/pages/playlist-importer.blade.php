<x-filament-panels::page>
    <form wire:submit="fetchLinks">
        {{ $this->form }}

        <div style="margin-top: 1rem;">
            <x-filament::button type="submit" wire:loading.attr="disabled">
                <span wire:loading.remove wire:target="fetchLinks">Fetch Links</span>
                <span wire:loading wire:target="fetchLinks">Fetching... Please wait...</span>
            </x-filament::button>
        </div>
    </form>

    @if($extracted_links)
    <x-filament::section>
        <x-slot name="heading">Extracted Links</x-slot>

        <textarea wire:model="extracted_links" rows="10" id="links-textarea"
            style="width: 100%; border-radius: 0.5rem; border: 1px solid #d1d5db; padding: 0.5rem; font-family: monospace; font-size: 0.875rem; background: transparent; color: inherit;"></textarea>

        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
            <x-filament::button type="button" color="gray" onclick="navigator.clipboard.writeText(document.getElementById('links-textarea').value).then(() => alert('Copied to clipboard!'))">
                📋 Copy All
            </x-filament::button>

            <x-filament::button wire:click="addToQueue" color="success">
                🚀 Add All to Job Queue
            </x-filament::button>
        </div>
    </x-filament::section>
    @endif
</x-filament-panels::page>
