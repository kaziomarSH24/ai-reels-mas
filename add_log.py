filepath = 'app/Filament/Pages/ReelGenerator.php'
with open(filepath, 'r') as f:
    content = f.read()

target = '''} catch (\Exception $e) {
                    // Fail silently and just show English
                }'''
replacement = '''} catch (\Exception $e) {
                    \Illuminate\Support\Facades\Log::error("JIT Error: " . $e->getMessage());
                }
                if (isset($response) && !$response->successful()) {
                    \Illuminate\Support\Facades\Log::error("JIT API Error: " . $response->body());
                }'''

content = content.replace(target, replacement)
with open(filepath, 'w') as f:
    f.write(content)
print("Log added!")
