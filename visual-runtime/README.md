# 🖥️ OpenHands Visual Runtime

A disposable, isolated Linux desktop environment that streams to the browser, allowing users to watch AI agents work in real-time.

## 🎯 What It Does

- **Visual Agent Execution**: Watch AI agents perform tasks in a real desktop environment
- **Real-time Streaming**: Browser-based VNC viewer with noVNC
- **Session Recording**: Automatic recording of agent activities
- **Security Isolation**: Each session runs in an isolated container
- **Take Control**: Users can optionally take control during agent execution

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Browser       │    │   Control Plane  │    │   Visual Runtime│
│                 │    │                  │    │                 │
│ • noVNC Canvas  │◄───┤ • Session API    │◄───┤ • Xvfb Display  │
│ • Live Controls │    │ • Container Mgmt │    │ • Fluxbox WM    │
│ • Recording     │    │ • Security       │    │ • Chromium      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenHands server running on port 3000

### 1. Build Visual Runtime Image
```bash
cd visual-runtime
docker build -t openhands/visual-runtime .
```

### 2. Start Visual Runtime
```bash
docker-compose up -d visual-runtime
```

### 3. Test the API
```bash
python test_visual.py
```

### 4. Access the Desktop
Open your browser to: `http://localhost:7900/vnc.html`

## 🔧 API Usage

### Create a Visual Session
```bash
curl -X POST http://localhost:3000/api/visual-sessions \
  -H "Content-Type: application/json" \
  -d '{
    "resolution": "1600x900",
    "timeout_minutes": 60,
    "idle_timeout_minutes": 15,
    "enable_recording": true,
    "enable_file_transfer": true
  }'
```

### Get Session Details
```bash
curl http://localhost:3000/api/visual-sessions/{session_id}
```

### Stop Session
```bash
curl -X POST http://localhost:3000/api/visual-sessions/{session_id}/stop
```

## 🛠️ Components

### Docker Container Includes:
- **Xvfb**: Virtual framebuffer X server
- **Fluxbox**: Lightweight window manager
- **x11vnc**: VNC server for X11 display
- **noVNC**: HTML5 VNC client
- **Chromium**: Web browser for agent tasks
- **xterm**: Terminal emulator
- **ffmpeg**: Session recording
- **OpenHands Agent**: AI agent runtime

### Security Features:
- Non-root user execution
- Container isolation
- Session timeouts
- Resource limits
- Network restrictions

## 📊 Session Management

Each visual session includes:
- **Unique Session ID**: Isolated environment per session
- **Time Limits**: Configurable timeout and idle timeout
- **Recording**: Automatic MP4 recording of desktop activity
- **Logs**: Session logs and agent activity tracking
- **Resource Limits**: CPU and memory constraints

## 🔒 Security Considerations

- **Container Isolation**: Each session runs in separate container
- **Network Restrictions**: Limited outbound access
- **User Privileges**: Non-root execution
- **Session Expiry**: Automatic cleanup
- **File Scanning**: Uploaded files are scanned

## 🎮 User Controls

### Browser Interface:
- **Visual Console**: Real-time desktop view
- **Take Control**: Pause agent and take manual control
- **Recording**: Download session recordings
- **Logs**: View agent activity logs
- **File Transfer**: Upload/download files

## 🚧 Current Limitations

- **Development Version**: Not production-hardened
- **Local Storage**: Recordings stored locally
- **Basic Security**: Advanced security features pending
- **Single User**: No multi-tenant support yet

## 🔮 Future Enhancements

- [ ] WebRTC streaming (lower latency)
- [ ] Kubernetes orchestration
- [ ] Advanced security (gVisor/Kata)
- [ ] Multi-tenant quotas
- [ ] Cloud storage integration
- [ ] GPU acceleration
- [ ] Advanced recording features

## 🐛 Troubleshooting

### Common Issues:

1. **Cannot connect to VNC**
   - Check if container is running: `docker ps`
   - Verify port 7900 is available
   - Check container logs: `docker logs openhands-visual-runtime`

2. **API endpoints not working**
   - Ensure OpenHands server is running on port 3000
   - Check if visual sessions API is registered
   - Verify no firewall blocking

3. **Recording not working**
   - Check ffmpeg installation in container
   - Verify disk space for recordings
   - Check file permissions

## 📝 Development

### Adding New Features:
1. Update Dockerfile with new packages
2. Add API endpoints in `visual_sessions.py`
3. Update startup scripts as needed
4. Test with `test_visual.py`
5. Update documentation

### Testing:
```bash
# Run full test suite
cd visual-runtime
python test_visual.py

# Manual API testing
curl -X POST http://localhost:3000/api/visual-sessions ...

# Container testing
docker-compose up --build
```

## 📄 License

Part of the OpenHands project. See main project LICENSE.