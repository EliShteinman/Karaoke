from dataclasses import dataclass
timestamp: float
text: str


def parse_lrc(lrc_text: str):
    lines = []
    for raw in lrc_text.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            if raw.startswith("["):
                parts = raw.split("]")
                for p in parts[:-1]:
                    ts = p.strip("[")
                    if ":" in ts:
                        mm, ss = ts.split(":")
                        sec = 0.0
                        if "." in ss:
                            s, ms = ss.split(".")
                            sec = int(mm) * 60 + int(s) + float("0." + ms)
                        else:
                            sec = int(mm) * 60 + int(ss)
                        text = parts[-1].strip()
                        lines.append(LrcLine(timestamp=sec, text=text))
        except Exception:
            continue
    lines.sort(key=lambda x: x.timestamp)
    return lines