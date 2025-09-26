from scanner import run_scanner
import yaml


def load_targets_from_config(config_path: str) -> list:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        targets = (data.get("scan") or {}).get("target_domains") or []
        return targets
    except FileNotFoundError:
        return []


if __name__ == "__main__":
    targets = load_targets_from_config("config/config.yaml")
    if targets:
        for domain in targets:
            run_scanner(domain)
    else:
        target = input("Enter target domain: ")
        run_scanner(target)

