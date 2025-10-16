FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install base packages
RUN apt-get update && apt-get install -y \
    supervisor xvfb x11vnc fluxbox net-tools wget curl python3 python3-pip \
    tigervnc-standalone-server tigervnc-common novnc websockify \
    chromium-browser xterm ffmpeg ca-certificates git sudo \
    file-manager gedit vim nano firefox \
 && rm -rf /var/lib/apt/lists/*

# noVNC static path
ENV NOVNC_HOME=/usr/share/novnc \
    WEB=/usr/share/novnc \
    DISPLAY=:1 \
    VNC_PORT=5901 \
    RESOLUTION=1600x900

# Create user
RUN useradd -ms /bin/bash runner && usermod -aG sudo runner && \
    echo "runner ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER runner
WORKDIR /home/runner

# Copy OpenHands worker files
COPY --chown=runner:runner openhands/ /home/runner/openhands/

# Install OpenHands dependencies
RUN cd /home/runner/openhands && pip3 install -e .

# Create startup scripts
USER root

# Main startup script
RUN bash -c 'cat >/usr/local/bin/start-visual.sh <<EOF
#!/usr/bin/env bash
set -e

export DISPLAY=:1
export RESOLUTION=${RESOLUTION:-1600x900}

# Start Xvfb (virtual display)
echo "Starting Xvfb..."
Xvfb :1 -screen 0 ${RESOLUTION}x24 -nolisten tcp &
XVFB_PID=$!

# Wait for Xvfb to start
sleep 2

# Start window manager
echo "Starting Fluxbox..."
fluxbox &
FLUXBOX_PID=$!

# Start VNC server
echo "Starting VNC server..."
x11vnc -display :1 -rfbport ${VNC_PORT} -forever -shared -nopw -quiet &
VNC_PID=$!

# Start noVNC proxy
echo "Starting noVNC proxy..."
/usr/share/novnc/utils/novnc_proxy --vnc localhost:${VNC_PORT} --listen 0.0.0.0:7900 &
NOVNC_PID=$!

# Start recording
echo "Starting session recording..."
ffmpeg -y -f x11grab -video_size ${RESOLUTION} -i ${DISPLAY}.0 -r 20 /home/runner/session.mp4 >/dev/null 2>&1 &
FFMPEG_PID=$!

# Launch desktop applications
echo "Starting desktop applications..."
sudo -u runner bash -lc "
    # Start terminal
    xterm &
    
    # Start Chromium (for web tasks)
    chromium-browser --no-sandbox --disable-dev-shm-usage --start-maximized &
    
    # Start file manager
    pcmanfm &
    
    # Start OpenHands worker
    echo 'Starting OpenHands agent...'
    cd /home/runner/openhands
    python3 -m openhands.server --visual-mode &
"

echo "Visual Runtime started successfully!"
echo "VNC available at: localhost:${VNC_PORT}"
echo "noVNC available at: http://localhost:7900/vnc.html"
echo "Session recording: /home/runner/session.mp4"

# Wait for processes
wait $XVFB_PID
EOF'

RUN chmod +x /usr/local/bin/start-visual.sh

# Supervisor configuration
RUN bash -c 'cat >/etc/supervisor/conf.d/visual.conf <<EOF
[supervisord]
nodaemon=true

[program:xvfb]
command=Xvfb :1 -screen 0 1600x900x24
user=runner

[program:fluxbox]
command=fluxbox
user=runner
environment=DISPLAY=:1

[program:vnc]
command=x11vnc -display :1 -rfbport 5901 -forever -shared -nopw -quiet
user=runner

[program:novnc]
command=/usr/share/novnc/utils/novnc_proxy --vnc localhost:5901 --listen 0.0.0.0:7900
user=runner

[program:recording]
command=ffmpeg -y -f x11grab -video_size 1600x900 -i :1.0 -r 20 /home/runner/session.mp4
user=runner

[program:openhands]
command=sudo -u runner bash -c "cd /home/runner/openhands && python3 -m openhands.server --visual-mode"
user=root
environment=DISPLAY=:1
EOF'

EXPOSE 7900

# Use supervisor to manage all processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]