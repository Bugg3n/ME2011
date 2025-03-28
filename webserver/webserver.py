import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import sys
from main import create_schedule

class ScheduleServer(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

class ScheduleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('monthly_schedule.html', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/calculate':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                params = json.loads(post_data)


                schedule_html, _ = create_schedule(
                    web_mode=True,
                    web_params={
                        'sales_capacity': int(params['sales_capacity']),
                        'average_service_time': float(params['average_service_time']),
                        'target_wait_time': float(params['target_wait_time']),
                    }
                )
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'content': schedule_html}).encode())
                
            except Exception as e:
                self.send_error(400, f"Error processing request: {str(e)}")

def run_server():
    
    server = HTTPServer(('localhost', 8000), ScheduleServer)
    print("Server running at http://localhost:8000")
    
    # Automatically open browser
    webbrowser.open('http://localhost:8000')
    
    server.serve_forever()

def do_OPTIONS(self):
    self.send_response(200)
    self.send_header('Access-Control-Allow-Origin', '*')
    self.send_header('Access-Control-Allow-Methods', 'POST')
    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    self.end_headers()
