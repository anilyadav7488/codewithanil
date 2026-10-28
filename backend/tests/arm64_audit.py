import urllib.request
import json

def check_pypi_wheel(pkg_name):
    url = f"https://pypi.org/pypi/{pkg_name}/json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ARM64-Audit"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            version = data["info"]["version"]
            urls = data["releases"].get(version, [])
            aarch64_wheels = [u["filename"] for u in urls if "aarch64" in u["filename"] or "any.whl" in u["filename"]]
            has_native = any("aarch64" in f for f in aarch64_wheels)
            has_any = any("any.whl" in f for f in aarch64_wheels)
            sample_wheel = aarch64_wheels[0] if aarch64_wheels else "Source tar.gz only"
            return version, has_native or has_any, sample_wheel
    except Exception as e:
        return str(e), False, "error"

packages = [
    "torch", "transformers", "tokenizers", "safetensors",
    "numpy", "scipy", "scikit-learn", "pandas",
    "psycopg2-binary", "bcrypt", "reportlab", "pypdf", "python-docx", "fastapi", "uvicorn", "alembic"
]

print("-" * 80)
print(f"{'Package':<18} | {'Latest Ver':<12} | {'ARM64 Compatible':<18} | Sample Wheel")
print("-" * 80)
for p in packages:
    v, supported, sample = check_pypi_wheel(p)
    print(f"{p:<18} | {v:<12} | {str(supported):<18} | {sample[:40]}")
print("-" * 80)
