from pathlib import Path
from urllib.request import Request, urlopen


def download_pdf(url: str, destination: str | Path, timeout: int = 60) -> Path:
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "InCite/1.0 research platform"})
    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        payload = response.read()
    if not payload.startswith(b"%PDF") and "pdf" not in content_type.lower():
        raise ValueError("Source did not return a PDF document")
    target.write_bytes(payload)
    return target
