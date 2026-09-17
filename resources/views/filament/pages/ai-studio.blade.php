<x-filament-panels::page>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        brand: {"50":"#f0fdf4","100":"#dcfce7","200":"#bbf7d0","300":"#86efac","400":"#4ade80","500":"#22c55e","600":"#16a34a","700":"#15803d","800":"#166534","900":"#14532d"},
                    },
                    fontFamily: {
                        sans: ['Inter', 'system-ui', 'sans-serif'],
                    }
                }
            }
        }
    </script>

    <!-- Subtle Grid Background -->
    <div class="relative w-full max-w-6xl mx-auto pb-12 font-sans">
        
        <!-- Tech/Studio Grid Pattern -->
        <div class="absolute inset-0 z-0 opacity-[0.03] pointer-events-none" 
             style="background-image: radial-gradient(circle at 2px 2px, white 1px, transparent 0); background-size: 32px 32px;">
        </div>

        <div class="relative z-10 space-y-8">
            
            <!-- Modern Header Banner -->
            <div class="flex flex-col md:flex-row md:items-center justify-between bg-[#131315] border border-white/10 rounded-2xl p-8 shadow-sm">
                <div>
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-white/5 border border-white/10 text-gray-300 text-xs font-medium mb-4">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                        Engine v2.0 Online
                    </div>
                    <h1 class="text-4xl font-bold tracking-tight text-white mb-2">
                        SnapClip <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-500">AI Studio</span>
                    </h1>
                    <p class="text-gray-400 text-base max-w-2xl">
                        Zero-storage video repurposing engine. Paste a YouTube link to extract dialogues, or generate a reel from specific words.
                    </p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                <!-- Phase 1: The Analyzer -->
                <div class="bg-[#131315] border border-white/10 rounded-2xl p-1 relative overflow-hidden group">
                    <!-- Subtle Hover Gradient Border -->
                    <div class="absolute inset-0 bg-gradient-to-b from-emerald-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    
                    <div class="relative bg-[#18181b] rounded-xl p-7 h-full flex flex-col justify-between">
                        <div>
                            <div class="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-5 text-emerald-400">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                            </div>
                            <h3 class="text-xl font-semibold text-white mb-2">1. The Analyzer</h3>
                            <p class="text-gray-400 text-sm mb-8 leading-relaxed">
                                Fetch subtitles, detect emotions, and save precise timestamps directly from a YouTube video URL.
                            </p>
                            
                            <div class="space-y-2">
                                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-widest">YouTube URL</label>
                                <div class="relative">
                                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <svg class="w-5 h-5 text-gray-500" fill="currentColor" viewBox="0 0 24 24"><path d="M21.582,6.186c-0.23-0.86-0.908-1.538-1.768-1.768C18.254,4,12,4,12,4S5.746,4,4.186,4.418c-0.86,0.23-1.538,0.908-1.768,1.768C2,7.746,2,12,2,12s0,4.254,0.418,5.814c0.23,0.86,0.908,1.538,1.768,1.768C5.746,20,12,20,12,20s6.254,0,7.814-0.418c0.86-0.23,1.538-0.908,1.768-1.768C22,16.254,22,12,22,12S22,7.746,21.582,6.186z M9.996,15.005l0-6l5.22,3L9.996,15.005z"/></svg>
                                    </div>
                                    <input type="url" wire:model="youtubeUrl" class="w-full bg-black/40 border border-white/10 rounded-lg pl-10 pr-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 transition-all shadow-inner" placeholder="https://youtube.com/watch?v=...">
                                </div>
                            </div>
                        </div>
                        
                        <button wire:click="analyzeVideo" class="mt-8 w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-3 px-4 rounded-lg transition-colors flex justify-center items-center gap-2 text-sm shadow-lg shadow-emerald-900/50">
                            Extract & Analyze
                        </button>
                    </div>
                </div>

                <!-- Phase 2: The Generator -->
                <div class="bg-[#131315] border border-white/10 rounded-2xl p-1 relative overflow-hidden group">
                    <!-- Subtle Hover Gradient Border -->
                    <div class="absolute inset-0 bg-gradient-to-b from-blue-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    
                    <div class="relative bg-[#18181b] rounded-xl p-7 h-full flex flex-col justify-between">
                        <div>
                            <div class="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mb-5 text-blue-400">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
                            </div>
                            <h3 class="text-xl font-semibold text-white mb-2">2. Reel Generator</h3>
                            <p class="text-gray-400 text-sm mb-8 leading-relaxed">
                                Search for a hard word (e.g. "Inevitable"). FFmpeg will dynamically stream clips from YouTube and render a 9:16 Reel.
                            </p>
                            
                            <div class="space-y-2">
                                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-widest">Target Word</label>
                                <div class="relative">
                                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                                    </div>
                                    <input type="text" wire:model="searchWord" class="w-full bg-black/40 border border-white/10 rounded-lg pl-10 pr-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all shadow-inner" placeholder="e.g. Inevitable">
                                </div>
                            </div>
                        </div>
                        
                        <button wire:click="generateReel" class="mt-8 w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 px-4 rounded-lg transition-colors flex justify-center items-center gap-2 text-sm shadow-lg shadow-blue-900/50">
                            Generate Magic Reel
                        </button>
                    </div>
                </div>

            </div>
        </div>
    </div>
</x-filament-panels::page>

@script
<script>
    let isProcessing = false;

    Livewire.hook('commit', ({ component, commit, respond, succeed, fail }) => {
        if (commit.calls.some(call => call.method === 'analyzeVideo')) {
            isProcessing = true;
        }
        succeed(({ snapshot, effect }) => {
            if (commit.calls.some(call => call.method === 'analyzeVideo')) {
                isProcessing = false;
            }
        });
        fail(() => {
            isProcessing = false;
        });
    });

    window.addEventListener('beforeunload', function (e) {
        if (isProcessing) {
            e.preventDefault();
            e.returnValue = 'AI is processing the video. Are you sure you want to leave?';
            return e.returnValue;
        }
    });

    document.addEventListener('livewire:navigating', (e) => {
        if (isProcessing) {
            if (!confirm('AI is processing the video. Are you sure you want to leave?')) {
                e.preventDefault();
            }
        }
    });
</script>
@endscript
