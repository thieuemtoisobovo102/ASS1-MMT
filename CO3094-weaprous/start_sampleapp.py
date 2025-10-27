#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
#
# WeApRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#


"""
start_sampleapp
~~~~~~~~~~~~~~~~~

This module provides a sample RESTful web application using the WeApRous framework.

It defines basic route handlers and launches a TCP-based backend server to serve
HTTP requests. The application includes a login endpoint and a greeting endpoint,
and can be configured via command-line arguments.
"""

import json
import socket
import argparse
import threading

from daemon.weaprous import WeApRous

PORT = 8000  # Default port

app = WeApRous()
peer_list = {}
peer_lock = threading.Lock()

@app.route('/submit-info', methods=['POST'])
def submit_info(headers, body):
    """
    Xử lý việc peer mới đăng ký hoặc cập nhật thông tin.
    Peer sẽ gửi một JSON body chứa thông tin của họ.
    """
    print(f"[SampleApp] Nhận /submit-info, body: {body[:50]}...")
    try:
        # 1. Phân tích (parse) JSON từ body
        data = json.loads(body)
        peer_id = data.get('id')
        peer_ip = data.get('ip')
        peer_port = data.get('port')

        if not peer_id or not peer_ip or not peer_port:
            return {"status": "error", "message": "Thiếu thông tin 'id', 'ip', hoặc 'port'"}

        # 2. Dùng lock để cập nhật danh sách một cách an toàn
        with peer_lock:
            peer_list[peer_id] = {"ip": peer_ip, "port": peer_port}
        
        print(f"[SampleApp] Đã đăng ký peer {peer_id} tại {peer_ip}:{peer_port}")
        # 3. Trả về thông báo thành công (sẽ được gửi lại dưới dạng JSON)
        return {"status": "success", "message": f"Peer {peer_id} đã đăng ký"}

    except json.JSONDecodeError:
        return {"status": "error", "message": "Body không phải là JSON hợp lệ"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/get-list', methods=['GET'])
def get_list(headers, body):
    """
    Trả về danh sách tất cả các peer đang hoạt động.
    """
    print("[SampleApp] Nhận /get-list")
    with peer_lock:
        # Trả về một bản sao (copy) của danh sách
        current_peers = dict(peer_list)
    
    return {"status": "success", "peers": current_peers}

@app.route('/login', methods=['POST'])
def login(headers="guest", body="anonymous"):
    """
    Handle user login via POST request.

    This route simulates a login process and prints the provided headers and body
    to the console.

    :param headers (str): The request headers or user identifier.
    :param body (str): The request body or login payload.
    """
    print("[SampleApp] Logging in {} to {}".format(headers, body))

@app.route('/hello', methods=['PUT'])
def hello(headers, body):
    """
    Handle greeting via PUT request.

    This route prints a greeting message to the console using the provided headers
    and body.

    :param headers (str): The request headers or user identifier.
    :param body (str): The request body or message payload.
    """
    print ("[SampleApp] ['PUT'] Hello in {} to {}".format(headers, body))

if __name__ == "__main__":
    # Parse command-line arguments to configure server IP and port
    parser = argparse.ArgumentParser(prog='Backend', description='', epilog='Beckend daemon')
    parser.add_argument('--server-ip', default='0.0.0.0')
    parser.add_argument('--server-port', type=int, default=PORT)
 
    args = parser.parse_args()
    ip = args.server_ip
    port = args.server_port

    # Prepare and launch the RESTful application
    app.prepare_address(ip, port)
    app.run()