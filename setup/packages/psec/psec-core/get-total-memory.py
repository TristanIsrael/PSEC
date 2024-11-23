import subprocess

def get_total_memory_with_xl():
    result = subprocess.run(['xl', 'info'], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if line.startswith("total_memory"):
            return int(line.split(':')[1].strip()) * 1024  # Convertir en kB
    return None

memory_kb = get_total_memory_with_xl()
if memory_kb:
    print(round(memory_kb / 1024))
else:
    print(0)
    