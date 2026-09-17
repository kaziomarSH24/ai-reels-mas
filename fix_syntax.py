with open("python_engine/app/services/video_service.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "f.write(f\"file '{pf}'" in line:
        lines[i] = "                f.write(f\"file '{pf}'\\n\")\n"
        # delete the next line if it is just '")'
        if i + 1 < len(lines) and '")' in lines[i+1]:
            lines[i+1] = ""

with open("python_engine/app/services/video_service.py", "w") as f:
    f.writelines(lines)
