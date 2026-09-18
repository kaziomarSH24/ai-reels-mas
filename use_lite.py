filepath = 'app/Filament/Pages/ReelGenerator.php'
with open(filepath, 'r') as f:
    content = f.read()

content = content.replace('gemini-3.5-flash', 'gemini-3.5-flash-lite')

with open(filepath, 'w') as f:
    f.write(content)

filepath_py = 'python_engine/app/services/video_service.py'
with open(filepath_py, 'r') as f:
    content_py = f.read()

content_py = content_py.replace('gemini-1.5-flash', 'gemini-3.5-flash-lite')

with open(filepath_py, 'w') as f:
    f.write(content_py)

print("Switched to gemini-3.5-flash-lite successfully!")
