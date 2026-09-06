<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Emotion Detector (Hunter Agent)</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen flex items-center justify-center font-sans">
    
    <div class="bg-gray-800 p-8 rounded-xl shadow-2xl w-full max-w-lg border border-gray-700">
        
        <div class="flex items-center mb-6">
            <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-2xl mr-4">
                🤖
            </div>
            <div>
                <h1 class="text-2xl font-bold text-blue-400">Hunter Agent Core</h1>
                <p class="text-gray-400 text-sm">Powered by DistilBERT (Kaggle)</p>
            </div>
        </div>

        <form action="{{ route('detect.emotion') }}" method="POST" class="space-y-4">
            @csrf
            
            <div>
                <label for="sentence" class="block text-sm font-medium text-gray-300 mb-1">
                    Enter a movie dialogue:
                </label>
                <textarea 
                    id="sentence" 
                    name="sentence" 
                    rows="3" 
                    class="w-full bg-gray-700 border border-gray-600 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
                    placeholder="e.g. I am completely fed up with your nonsense!"
                    required
                >{{ session('sentence') }}</textarea>
            </div>

            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition duration-200 flex justify-center items-center">
                Analyze Emotion <span class="ml-2">⚡</span>
            </button>
        </form>

        @if(session('result'))
            <div class="mt-8 p-5 bg-gray-900 rounded-lg border border-gray-700">
                <h3 class="text-sm text-gray-400 uppercase tracking-wider mb-3">AI Analysis Result</h3>
                
                @if(isset(session('result')['error']))
                    <div class="text-red-400 flex items-center">
                        <span class="text-xl mr-2">❌</span>
                        {{ session('result')['error'] }}
                    </div>
                @else
                    @php
                        $emotion = session('result')['emotion'] ?? 'UNKNOWN';
                        $confidence = session('result')['confidence'] ?? 0;
                        
                        $emoji = '😐';
                        $color = 'text-gray-300';
                        
                        if($emotion == 'JOY') { $emoji = '😁'; $color = 'text-green-400'; }
                        if($emotion == 'ANGER') { $emoji = '😡'; $color = 'text-red-500'; }
                        if($emotion == 'SADNESS') { $emoji = '😢'; $color = 'text-blue-400'; }
                        if($emotion == 'SURPRISE') { $emoji = '😲'; $color = 'text-yellow-400'; }
                        if($emotion == 'FEAR') { $emoji = '😨'; $color = 'text-purple-400'; }
                        if($emotion == 'LOVE') { $emoji = '❤️'; $color = 'text-pink-400'; }
                    @endphp
                    
                    <div class="flex justify-between items-center mb-4">
                        <span class="text-gray-300">Detected Emotion:</span>
                        <span class="text-2xl font-bold {{ $color }}">{{ $emotion }} {{ $emoji }}</span>
                    </div>
                    
                    <div class="mb-4">
                        <div class="flex justify-between text-sm mb-1">
                            <span class="text-gray-400">Confidence</span>
                            <span class="text-blue-400 font-mono">{{ $confidence }}%</span>
                        </div>
                        <div class="w-full bg-gray-700 rounded-full h-2">
                            <div class="bg-blue-500 h-2 rounded-full" style="width: {{ $confidence }}%"></div>
                        </div>
                    </div>
                    
                    <div class="flex justify-between items-center mb-4 p-3 bg-gray-800 rounded border border-gray-700">
                        <span class="text-gray-300">CEFR Difficulty Level:</span>
                        <span class="text-xl font-bold text-yellow-400">{{ session('result')['cefr_level'] ?? 'N/A' }}</span>
                    </div>

                    <div class="bg-gray-800 p-4 rounded-lg border border-gray-600">
                        <div class="text-xs text-blue-400 uppercase tracking-wider mb-1">Bangla Translation (Teacher Agent)</div>
                        <p class="text-lg text-white font-medium">{{ session('result')['translation'] ?? 'Translation failed' }}</p>
                    </div>
                @endif
            </div>
        @endif
        
        <p class="text-xs text-gray-500 text-center mt-6">
            Note: Since the model is loaded on each request (No Queue), it may take 3-5 seconds to respond.
        </p>

    </div>
</body>
</html>
