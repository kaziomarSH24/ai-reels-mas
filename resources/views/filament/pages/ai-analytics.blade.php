<x-filament-panels::page>
    <div class="space-y-6">
        @if ($this->getHeaderWidgets())
            <x-filament-widgets::widgets
                :columns="$this->getHeaderWidgetsColumns()"
                :data="$this->getWidgetData()"
                :widgets="$this->getVisibleHeaderWidgets()"
            />
        @endif
    </div>
</x-filament-panels::page>
