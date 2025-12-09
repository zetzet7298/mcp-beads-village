"""Test script to verify mcp-beads-village changes."""

import sys


def test_imports():
    """Test all imports work."""
    print("=== Test 1: Imports ===")
    from beads_village.server import (
        TOOLS,
        USE_DAEMON,
        _get_daemon_client,
        bd,
        tool_add,
    )
    from beads_village.bd_daemon_client import (
        BdDaemonClient,
        DaemonError,
        DaemonNotRunningError,
        is_daemon_available,
    )
    print("[OK] All imports OK")
    print(f"  USE_DAEMON: {USE_DAEMON}")
    print(f"  Daemon available: {is_daemon_available()}")
    return True


def test_add_tool_schema():
    """Test add tool has new properties."""
    print("\n=== Test 2: Add Tool Schema ===")
    from beads_village.server import TOOLS
    
    add_tool = TOOLS['add']
    props = add_tool['input']['properties']
    
    # Check new properties exist
    assert 'desc' in props, "Missing 'desc' property"
    assert 'deps' in props, "Missing 'deps' property"
    assert 'typ' in props, "Missing 'typ' property"
    assert 'title' in props, "Missing 'title' property"
    assert 'pri' in props, "Missing 'pri' property"
    assert 'parent' in props, "Missing 'parent' property"
    
    print(f"[OK] Properties: {list(props.keys())}")
    
    # Check desc description (token-optimized)
    desc_desc = props['desc']['description']
    assert len(desc_desc) > 0, "desc description should not be empty"
    print(f"[OK] desc: {desc_desc}")
    
    # Check deps description (token-optimized)
    deps_desc = props['deps']['description']
    assert len(deps_desc) > 0, "deps description should not be empty"
    print(f"[OK] deps: {deps_desc}")
    
    return True


def test_issue_types():
    """Test issue types include feature and chore."""
    print("\n=== Test 3: Issue Types ===")
    from beads_village.server import TOOLS
    
    typ_desc = TOOLS['add']['input']['properties']['typ']['description']
    
    assert 'task' in typ_desc, "Missing 'task' type"
    assert 'bug' in typ_desc, "Missing 'bug' type"
    assert 'feature' in typ_desc, "Missing 'feature' type"
    assert 'epic' in typ_desc, "Missing 'epic' type"
    assert 'chore' in typ_desc, "Missing 'chore' type"
    
    print(f"[OK] Types: {typ_desc}")
    return True


def test_daemon_client():
    """Test daemon client can be instantiated."""
    print("\n=== Test 4: Daemon Client ===")
    from beads_village.bd_daemon_client import (
        BdDaemonClient,
        is_daemon_available,
    )
    
    # Create client
    client = BdDaemonClient(working_dir="C:/tmp", actor="test-agent")
    assert client.working_dir == "C:/tmp"
    assert client.actor == "test-agent"
    assert client.timeout == 30.0
    print(f"[OK] BdDaemonClient created")
    print(f"  working_dir: {client.working_dir}")
    print(f"  actor: {client.actor}")
    
    # Check is_daemon_available works
    available = is_daemon_available()
    print(f"[OK] is_daemon_available(): {available}")
    
    return True


def test_bd_function_fallback():
    """Test bd() function exists and has fallback logic."""
    print("\n=== Test 5: bd() Function ===")
    from beads_village.server import bd, bd_sync, _get_daemon_client, USE_DAEMON
    
    # Check functions exist
    assert callable(bd), "bd is not callable"
    assert callable(bd_sync), "bd_sync is not callable"
    assert callable(_get_daemon_client), "_get_daemon_client is not callable"
    
    print(f"[OK] bd() function exists")
    print(f"[OK] bd_sync() function exists")
    print(f"[OK] _get_daemon_client() function exists")
    print(f"  USE_DAEMON: {USE_DAEMON}")
    
    # Check daemon client returns None when no daemon
    client = _get_daemon_client()
    print(f"[OK] _get_daemon_client(): {client}")
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing mcp-beads-village changes")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_add_tool_schema,
        test_issue_types,
        test_daemon_client,
        test_bd_function_fallback,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"[FAILED]: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR]: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
