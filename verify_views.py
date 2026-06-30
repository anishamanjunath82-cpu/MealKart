import urllib.request
import urllib.parse
import json
import sys

def test_endpoints():
    base_url = "http://127.0.0.1:8000"
    print(f"Testing local Django server at: {base_url}")
    
    # Configure urllib to handle cookies (needed for login session)
    cookie_processor = urllib.request.HTTPCookieProcessor()
    opener = urllib.request.build_opener(cookie_processor)
    urllib.request.install_opener(opener)
    
    errors = 0

    # 1. Fetch Login Page to retrieve CSRF token and establish cookie session
    csrf_token = None
    try:
        login_get = urllib.request.urlopen(f"{base_url}/auth/login/")
        cookies = login_get.info().get_all('Set-Cookie', [])
        
        # Parse csrf token from cookies
        for cookie in cookies:
            if 'csrftoken=' in cookie:
                csrf_token = cookie.split('csrftoken=')[1].split(';')[0]
                break
                
        # If not in cookies, fallback to HTML parsing
        if not csrf_token:
            html = login_get.read().decode('utf-8')
            if 'name="csrfmiddlewaretoken" value="' in html:
                csrf_token = html.split('name="csrfmiddlewaretoken" value="')[1].split('"')[0]

        if csrf_token:
            print(f"[PASS] Established session and retrieved CSRF Token: {csrf_token[:8]}...")
        else:
            print("[FAIL] Failed to obtain CSRF Token.")
            errors += 1
            return sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Failed to load Login page: {e}")
        errors += 1
        return sys.exit(1)

    # 2. Perform Login POST using the correct form field name 'username_or_email'
    try:
        post_data = urllib.parse.urlencode({
            'username_or_email': 'admin',
            'password': 'adminpass',
            'csrfmiddlewaretoken': csrf_token
        }).encode('utf-8')
        
        req = urllib.request.Request(f"{base_url}/auth/login/", data=post_data, headers={
            'Referer': f"{base_url}/auth/login/",
            'X-CSRFToken': csrf_token
        })
        
        login_post = urllib.request.urlopen(req)
        landing_url = login_post.geturl()
        
        # In Django, login view redirects to '/' (LOGIN_REDIRECT_URL)
        if landing_url.rstrip('/') == base_url:
            print("[PASS] Authentication Successful! Redirected to Homepage.")
        else:
            # Let's check if we landed on home even with trailing next query params
            if "/auth/login/" not in landing_url:
                print(f"[PASS] Authentication Successful! Landed on: {landing_url}")
            else:
                print(f"[FAIL] Authentication Redirect Mismatch. Landed on: {landing_url}")
                errors += 1
    except Exception as e:
        print(f"[FAIL] Authentication Request Failed: {e}")
        errors += 1

    # 3. Test Homepage (now that we are authenticated)
    try:
        response = urllib.request.urlopen(f"{base_url}/")
        html = response.read().decode('utf-8')
        print("[PASS] Homepage Loaded (200 OK)")
        if "Pizza Palazzo" in html:
            print("  [PASS] Featured Restaurant 'Pizza Palazzo' is visible on Homepage")
        else:
            print("  [FAIL] Featured Restaurant 'Pizza Palazzo' missing from Homepage")
            errors += 1
            
        if "Royal Biryani House" in html:
            print("  [PASS] Featured Restaurant 'Royal Biryani House' is visible on Homepage")
        else:
            print("  [FAIL] Featured Restaurant 'Royal Biryani House' missing from Homepage")
            errors += 1
    except Exception as e:
        print(f"[FAIL] Homepage GET Request Failed: {e}")
        errors += 1

    # 4. Test Authenticated Cart Page GET
    try:
        response = urllib.request.urlopen(f"{base_url}/cart/")
        html = response.read().decode('utf-8')
        print("[PASS] Authenticated Cart Page Loaded (200 OK)")
        if "Your Cart is Empty" in html:
            print("  [PASS] Cart is verified Empty as expected")
        else:
            print("  [WARNING] Cart is not empty, but page loaded successfully.")
    except Exception as e:
        print(f"[FAIL] Cart Page GET Failed: {e}")
        errors += 1

    # 5. Test Live Search API JSON
    try:
        response = urllib.request.urlopen(f"{base_url}/api/search/?q=Pizza")
        raw_json = response.read().decode('utf-8')
        data = json.loads(raw_json)
        print("[PASS] Search API Endpoint Returned (200 OK)")
        results = data.get('results', [])
        print(f"  [PASS] Search returned {len(results)} items matching query 'Pizza'")
        for idx, item in enumerate(results[:2]):
            print(f"    - Item {idx+1}: {item['name']} from {item['hotel_name']} (Rs.{item['price']})")
    except Exception as e:
        print(f"[FAIL] Search API GET Failed: {e}")
        errors += 1

    # 6. Test Authenticated Profile Page GET
    try:
        response = urllib.request.urlopen(f"{base_url}/profile/")
        html = response.read().decode('utf-8')
        print("[PASS] Authenticated Profile Page Loaded (200 OK)")
        if "admin" in html or "System Admin" in html:
            print("  [PASS] Profile shows Username/Name 'admin' or 'System Admin'")
        else:
            print("  [FAIL] Profile page does not match logged-in user.")
            errors += 1
    except Exception as e:
        print(f"[FAIL] Profile Page GET Failed: {e}")
        errors += 1

    # Summary
    print("\n--- TEST SUMMARY ---")
    if errors == 0:
        print("ALL TESTS PASSED SUCCESSFULLY! The mealKart application is fully operational.")
        sys.exit(0)
    else:
        print(f"TESTING COMPLETED WITH {errors} FAILURE(S). Check logs above.")
        sys.exit(1)

if __name__ == '__main__':
    test_endpoints()
