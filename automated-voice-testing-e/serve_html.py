#!/usr/bin/env python3
"""
Simple HTTP server to serve HTML files on port 9867
"""
import http.server
import socketserver
import os

# Change to the directory containing the HTML files
os.chdir('/home/ubuntu/workspace/automated-testing')

PORT = 9867
HOST = '0.0.0.0'  # Listen on all interfaces for public IP access

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def log_message(self, format, *args):
        """Log each request"""
        print(f"{self.address_string()} - {format % args}")

if __name__ == "__main__":
    Handler = MyHTTPRequestHandler

    with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
        print(f"=" * 70)
        print(f"Server running on http://{HOST}:{PORT}")
        print(f"=" * 70)
        print(f"\nAvailable HTML files:")
        print(f"  • Dashboard:        http://<your-ip>:{PORT}/dashboard.html")
        print(f"  • Test Management:  http://<your-ip>:{PORT}/test-management.html")
        print(f"  • Reports:          http://<your-ip>:{PORT}/reports.html")
        print(f"  • Analytics:        http://<your-ip>:{PORT}/analytics.html")
        print(f"  • Validation:       http://<your-ip>:{PORT}/validation.html")
        print(f"  • Test Debug:       http://<your-ip>:{PORT}/test-debug.html")
        print(f"  • Index:            http://<your-ip>:{PORT}/index.html")
        print(f"\nPress Ctrl+C to stop the server")
        print(f"=" * 70)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
