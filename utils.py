def safe_int(s, default=None):
    try:
        return int(s)
    except Exception:
        return default

def confirm(prompt='Are you sure? (y/n): '):
    r = input(prompt).strip().lower()
    return r in ('y', 'yes')
