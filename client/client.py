import curses
import socket
import sys

def main(stdscr):
    user_input_buffer = ""
    server_output_buffer = ""
    if len(sys.argv)==3:
        server = sys.argv[1]
        port = sys.argv[2]
    else:
        # Clear screen
        stdscr.clear()
        stdscr.addstr(0,0,'Server: ')
        curses.echo()
        server = stdscr.getstr(curses.COLS-curses.getsyx()[1]).decode()
        stdscr.addstr('Port: ')
        port = stdscr.getstr(curses.COLS-curses.getsyx()[1]).decode()
    stdscr.nodelay(True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server, int(port)))
        sock.settimeout(0.02)
        while True:
            try:
                data = sock.recv(1024)
                if data.decode().strip() != '':
                    server_output_buffer += data.decode()
            except socket.timeout as e:
                uinput = stdscr.getch()
                if uinput != -1:
                    user_input_buffer += chr(uinput)
                if uinput == 10:
                    #send input buffer and clear it
                    send(sock, user_input_buffer.encode())
                    stdscr.erase()
                    user_input_buffer = ""
                if uinput == 263:
                    #backspace
                    user_input_buffer = user_input_buffer[:-2]
                    stdscr.clrtoeol()
            stdscr.addstr(2,0, server_output_buffer)
            stdscr.addstr(0,0, f"Server: {server}:{port}")
            stdscr.addstr(1,0, user_input_buffer)
            stdscr.clrtoeol()

    stdscr.refresh()
    stdscr.getkey()

def send(sock, msg):
    totalsent = 0
    while totalsent < len(msg):
        sent = sock.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent

curses.wrapper(main)
