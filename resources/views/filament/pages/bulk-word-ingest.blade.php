<x-filament-panels::page>
    <form wire:submit="start_bot" class="space-y-6">
        {{ $this->form }}

        <div class="mt-4">
            <x-filament::button type="submit" size="lg">
                Start Bot in Background
            </x-filament::button>
        </div>
    </form>
</x-filament-panels::page>
