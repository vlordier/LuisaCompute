import subprocess
from pathlib import Path

proj_dir = Path(__file__).parent.parent
dst_dir = proj_dir / 'src/runtime/backend_version.inl'

result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
out = result.stdout.replace('\r', '').replace('\n', '')
with open(dst_dir, 'w') as f:
    f.write(f'constexpr const char luisa_backend_version[] = "{out}";')
