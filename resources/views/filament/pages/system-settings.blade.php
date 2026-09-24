<x-filament-panels::page>
    <form wire:submit="save">
        {{ $this->form }}
        
        <div class="mt-4">
            <x-filament::button type="submit">
                Save Settings
            </x-filament::button>
        </div>
    </form>
    
    @if(file_exists(storage_path('app/cookies.txt')))
        <div class="mt-4 p-4 bg-green-100 text-green-800 rounded-lg">
            ✅ cookies.txt is currently active on the server.
        </div>
    @else
        <div class="mt-4 p-4 bg-red-100 text-red-800 rounded-lg">
            ❌ No cookies.txt found on the server.
        </div>
    @endif
</x-filament-panels::page>
