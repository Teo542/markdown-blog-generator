import argparse
import http.server
import os
import socket
import webbrowser

PORT = 8000
DIST_DIR = "dist"


def get_local_ip():
    """Get the local IP address for network access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    parser = argparse.ArgumentParser(description="Development server for the blog")
    parser.add_argument(
        '--network',
        action='store_true',
        help='Allow network access for mobile testing (binds to 0.0.0.0)'
    )
    args = parser.parse_args()

    host = "0.0.0.0" if args.network else "127.0.0.1"

    os.chdir(DIST_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    server = http.server.HTTPServer((host, PORT), handler)

    print(f"\n  Local: http://localhost:{PORT}")

    if args.network:
        local_ip = get_local_ip()
        print(f"  Network: http://{local_ip}:{PORT}")
        print(f"\n  Open the Network URL on your phone to test mobile view")
    else:
        print(f"\n  Use --network flag to enable mobile testing")

    print("  Press Ctrl+C to stop\n")

    webbrowser.open(f"http://localhost:{PORT}")
    server.serve_forever()


if __name__ == '__main__':
    main()
