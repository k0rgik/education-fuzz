import requests
import json
import sys

BASE_URL = "http://localhost:3000"
LOGIN_URL = f"{BASE_URL}/rest/user/login"

PAYLOADS = [
    "' OR 1=1--",
    "' OR '1'='1",
    "admin'--",
    "' OR 1=1;--",
    "' UNION SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13--",
]

def run_fuzz():
    results = []
    for payload in PAYLOADS:
        body = {"email": payload, "password": "any"}
        try:
            r = requests.post(LOGIN_URL, json=body, timeout=10)
            entry = {
                "payload": payload,
                "status_code": r.status_code,
                "vulnerable": False,
                "response_preview": r.text[:300],
            }
            if r.status_code == 200 and "authentication" in r.text:
                entry["vulnerable"] = True
                entry["details"] = "SQLi confirmed: got authentication token"
            results.append(entry)
        except Exception as e:
            results.append({"payload": payload, "error": str(e)})
    return results

if __name__ == "__main__":
    results = run_fuzz()
    with open("fuzz_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    vulnerable = [r for r in results if r.get("vulnerable")]
    print(f"Total payloads: {len(results)}")
    print(f"Vulnerable: {len(vulnerable)}")
    for v in vulnerable:
        print(f"  [!] SQLi found: {v['payload']} → HTTP {v['status_code']}")
    
    if vulnerable:
        # Это сработает в GitHub Actions как ошибка пайплайна
        print("::error::SQL Injection detected in /rest/user/login")
        sys.exit(1)
    else:
        print("::notice::No SQLi detected")
        sys.exit(0)
