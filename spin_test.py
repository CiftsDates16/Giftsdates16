#!/usr/bin/env python3
"""
Backend test for GiftsDates Spin-to-Win 5-coin consolation prize.
Tests that when a user's welcome spin result is "none", they receive 5 coins.
"""
import requests
import random
import time
from datetime import datetime

BASE_URL = "https://gift-saver-2.preview.emergentagent.com/api"

def generate_test_user():
    """Generate a unique test user with realistic data."""
    timestamp = int(time.time())
    random_num = random.randint(1000, 9999)
    
    # Generate birth date for someone 18+ years old (between 18-40 years old)
    current_year = datetime.now().year
    birth_year = current_year - random.randint(18, 40)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)  # Safe day that works for all months
    
    first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn", "Skylar", "Dakota", "Reese", "Cameron", "Sage", "River", "Phoenix"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Wilson", "Anderson", "Taylor", "Thomas", "Moore"]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
    genders = ["male", "female", "non_binary"]
    orientations = ["straight", "gay", "lesbian", "bisexual", "pansexual"]
    
    gender = random.choice(genders)
    interested_in = random.choice(["male", "female", "everyone"])
    
    return {
        "email": f"{first_name.lower()}.{last_name.lower()}.{timestamp}{random_num}@gmail.com",
        "password": f"SecurePass{random_num}!",
        "name": f"{first_name} {last_name}",
        "age": current_year - birth_year,
        "birth_year": birth_year,
        "birth_month": birth_month,
        "birth_day": birth_day,
        "gender": gender,
        "interested_in": interested_in,
        "orientation": random.choice(orientations),
        "city": random.choice(cities),
        "country": "USA",
        "bio": f"Test user for spin-to-win testing",
        "language": "en"
    }

def register_user(user_data):
    """Register a new user and return token and user info."""
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data, timeout=30)
        response.raise_for_status()
        data = response.json()
        return {
            "success": True,
            "token": data.get("token"),
            "user_id": data.get("user", {}).get("id"),
            "email": user_data["email"],
            "name": user_data["name"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "email": user_data["email"]
        }

def claim_spin(token):
    """Claim the welcome spin for a user."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/spin/claim", headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return {
            "success": True,
            "prize": data.get("prize", {}),
            "status_code": response.status_code
        }
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": e.response.status_code if e.response else None,
            "response": e.response.text if e.response else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": None
        }

def get_user_profile(token):
    """Get user profile to verify coin balance."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return {
            "success": True,
            "coins": data.get("coins", 0),
            "user_id": data.get("id"),
            "name": data.get("name")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    print("=" * 80)
    print("GiftsDates Spin-to-Win Backend Test")
    print("Testing 5-coin consolation prize for 'no win' results")
    print("=" * 80)
    print()
    
    # Test configuration
    NUM_USERS = 15
    results = {
        "none": [],
        "coins": [],
        "premium_lite": [],
        "premium": [],
        "vip": [],
        "errors": []
    }
    
    print(f"Registering {NUM_USERS} new users and testing spin-to-win...")
    print()
    
    for i in range(NUM_USERS):
        print(f"[{i+1}/{NUM_USERS}] ", end="", flush=True)
        
        # Generate and register user
        user_data = generate_test_user()
        reg_result = register_user(user_data)
        
        if not reg_result["success"]:
            print(f"❌ Registration failed: {reg_result['error']}")
            results["errors"].append({
                "step": "registration",
                "email": reg_result["email"],
                "error": reg_result["error"]
            })
            continue
        
        print(f"✓ Registered {reg_result['name']} ({reg_result['email'][:30]}...)", end=" ", flush=True)
        
        # Claim spin
        spin_result = claim_spin(reg_result["token"])
        
        if not spin_result["success"]:
            print(f"❌ Spin claim failed: {spin_result['error']}")
            results["errors"].append({
                "step": "spin_claim",
                "user_id": reg_result["user_id"],
                "email": reg_result["email"],
                "error": spin_result["error"],
                "status_code": spin_result.get("status_code")
            })
            continue
        
        prize = spin_result["prize"]
        prize_type = prize.get("type")
        prize_coins = prize.get("coins")
        
        print(f"→ Spin: {prize_type}", end=" ", flush=True)
        
        # Get user profile to verify coins
        profile = get_user_profile(reg_result["token"])
        
        if not profile["success"]:
            print(f"❌ Profile fetch failed: {profile['error']}")
            results["errors"].append({
                "step": "profile_fetch",
                "user_id": reg_result["user_id"],
                "error": profile["error"]
            })
            continue
        
        actual_coins = profile["coins"]
        
        # Store result
        result_entry = {
            "user_id": reg_result["user_id"],
            "name": reg_result["name"],
            "email": reg_result["email"],
            "prize_type": prize_type,
            "prize_coins": prize_coins,
            "actual_coins": actual_coins,
            "prize_data": prize
        }
        
        # Validate based on prize type
        if prize_type == "none":
            if prize_coins == 5 and actual_coins == 5:
                print(f"✅ Coins: {actual_coins} (PASS)")
                result_entry["validation"] = "PASS"
            else:
                print(f"❌ Coins: expected 5, got prize_coins={prize_coins}, actual={actual_coins} (FAIL)")
                result_entry["validation"] = "FAIL"
                result_entry["error"] = f"Expected 5 coins, got prize_coins={prize_coins}, actual={actual_coins}"
            results["none"].append(result_entry)
            
        elif prize_type == "coins":
            if prize_coins == 10 and actual_coins == 10:
                print(f"✅ Coins: {actual_coins} (PASS)")
                result_entry["validation"] = "PASS"
            else:
                print(f"❌ Coins: expected 10, got prize_coins={prize_coins}, actual={actual_coins} (FAIL)")
                result_entry["validation"] = "FAIL"
                result_entry["error"] = f"Expected 10 coins, got prize_coins={prize_coins}, actual={actual_coins}"
            results["coins"].append(result_entry)
            
        elif prize_type in ["premium_lite", "premium", "vip"]:
            # For tier prizes, coins should be 0 (no coins awarded, just tier)
            expires_at = prize.get("expires_at")
            if expires_at:
                print(f"✅ Tier granted, expires: {expires_at[:10]} (PASS)")
                result_entry["validation"] = "PASS"
                result_entry["expires_at"] = expires_at
            else:
                print(f"❌ Tier granted but no expiry (FAIL)")
                result_entry["validation"] = "FAIL"
                result_entry["error"] = "Tier granted but no expires_at field"
            results[prize_type].append(result_entry)
        
        else:
            print(f"⚠️  Unknown prize type: {prize_type}")
            results["errors"].append({
                "step": "unknown_prize_type",
                "user_id": reg_result["user_id"],
                "prize_type": prize_type,
                "prize": prize
            })
        
        # Small delay to avoid rate limiting
        time.sleep(0.2)
    
    # Print summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    
    print(f"Total users tested: {NUM_USERS}")
    print(f"Errors: {len(results['errors'])}")
    print()
    
    print("Prize Distribution:")
    print(f"  - 'none' (Try Again): {len(results['none'])} users")
    print(f"  - 'coins' (10 coins): {len(results['coins'])} users")
    print(f"  - 'premium_lite': {len(results['premium_lite'])} users")
    print(f"  - 'premium': {len(results['premium'])} users")
    print(f"  - 'vip': {len(results['vip'])} users")
    print()
    
    # Detailed results for "none" prizes
    if results["none"]:
        print("=" * 80)
        print("DETAILED RESULTS: 'none' (Try Again) - 5 Coin Consolation")
        print("=" * 80)
        passed = [r for r in results["none"] if r.get("validation") == "PASS"]
        failed = [r for r in results["none"] if r.get("validation") == "FAIL"]
        
        print(f"✅ PASSED: {len(passed)}/{len(results['none'])}")
        for r in passed:
            print(f"   - {r['name']}: prize_coins={r['prize_coins']}, actual_coins={r['actual_coins']}")
        
        if failed:
            print(f"❌ FAILED: {len(failed)}/{len(results['none'])}")
            for r in failed:
                print(f"   - {r['name']}: {r.get('error', 'Unknown error')}")
        print()
    
    # Detailed results for "coins" prizes
    if results["coins"]:
        print("=" * 80)
        print("DETAILED RESULTS: 'coins' (10 Coins)")
        print("=" * 80)
        passed = [r for r in results["coins"] if r.get("validation") == "PASS"]
        failed = [r for r in results["coins"] if r.get("validation") == "FAIL"]
        
        print(f"✅ PASSED: {len(passed)}/{len(results['coins'])}")
        for r in passed:
            print(f"   - {r['name']}: prize_coins={r['prize_coins']}, actual_coins={r['actual_coins']}")
        
        if failed:
            print(f"❌ FAILED: {len(failed)}/{len(results['coins'])}")
            for r in failed:
                print(f"   - {r['name']}: {r.get('error', 'Unknown error')}")
        print()
    
    # Tier prizes
    for tier in ["premium_lite", "premium", "vip"]:
        if results[tier]:
            print("=" * 80)
            print(f"DETAILED RESULTS: '{tier}' Tier")
            print("=" * 80)
            passed = [r for r in results[tier] if r.get("validation") == "PASS"]
            failed = [r for r in results[tier] if r.get("validation") == "FAIL"]
            
            print(f"✅ PASSED: {len(passed)}/{len(results[tier])}")
            for r in passed:
                print(f"   - {r['name']}: expires {r.get('expires_at', 'N/A')[:10]}")
            
            if failed:
                print(f"❌ FAILED: {len(failed)}/{len(results[tier])}")
                for r in failed:
                    print(f"   - {r['name']}: {r.get('error', 'Unknown error')}")
            print()
    
    # Errors
    if results["errors"]:
        print("=" * 80)
        print("ERRORS")
        print("=" * 80)
        for err in results["errors"]:
            print(f"❌ {err.get('step', 'unknown')}: {err.get('error', 'Unknown error')}")
            if err.get("status_code"):
                print(f"   Status code: {err['status_code']}")
        print()
    
    # Final verdict
    print("=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)
    
    total_none = len(results["none"])
    passed_none = len([r for r in results["none"] if r.get("validation") == "PASS"])
    
    total_coins = len(results["coins"])
    passed_coins = len([r for r in results["coins"] if r.get("validation") == "PASS"])
    
    total_tiers = len(results["premium_lite"]) + len(results["premium"]) + len(results["vip"])
    passed_tiers = len([r for r in results["premium_lite"] + results["premium"] + results["vip"] if r.get("validation") == "PASS"])
    
    print(f"✅ 'none' (5 coins): {passed_none}/{total_none} passed")
    print(f"✅ 'coins' (10 coins): {passed_coins}/{total_coins} passed")
    print(f"✅ Tier prizes: {passed_tiers}/{total_tiers} passed")
    print(f"❌ Errors: {len(results['errors'])}")
    print()
    
    if passed_none == total_none and passed_coins == total_coins and passed_tiers == total_tiers and len(results["errors"]) == 0:
        print("🎉 ALL TESTS PASSED! The 5-coin consolation prize is working correctly.")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED. Review the detailed results above.")
        return 1

if __name__ == "__main__":
    exit(main())
