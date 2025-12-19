import requests

def test_metadata():
    # This is the URL from the user's log
    url = "https://ek949jg.cloudatacdn.com/u5kjxw3i67c3sdgge4474o2pj3sqzcmrj5w2qm7gc3kq6j6zplu5q2ib545q/5uo8x30kis~iBTrO81TLZ?token=agujwn61325nbjwtqq8584b9&expiry=1766106346095"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://play.cuevana3cc.me/'
    }
    
    print(f"Probing URL: {url}")
    try:
        # Try HEAD request first
        response = requests.head(url, headers=headers, verify=False, allow_redirects=True, timeout=10)
        print(f"Status Code: {response.status_code}")
        print("Headers:")
        for k, v in response.headers.items():
            print(f"  {k}: {v}")
            
        cl = response.headers.get('Content-Length')
        if cl:
            size_mb = int(cl) / (1024 * 1024)
            print(f"Content-Length found: {cl} bytes ({size_mb:.2f} MB)")
        else:
            print("No Content-Length header found.")
            
    except Exception as e:
        print(f"Probe failed: {e}")

if __name__ == "__main__":
    test_metadata()
