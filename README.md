# HV CTF Platform

This repository contains the first steps toward a custom Capture The Flag (CTF) platform based on [CTFd](https://github.com/CTFd/CTFd). The goal is to implement a minimal Flask application and gradually extend it with challenge management, scoring, and event features.

## Development

1. Create a Python virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run the development server:

```bash
python -m hv_ctf.app
```

This will start a basic Flask app with SQLite database support. The app now
renders HTML templates for registration, login, challenges, and the scoreboard.
Users can create and join teams, solve challenges, and view scores for both
teams and individuals.


- [x] Support plugins and custom challenge types

- [ ] Integrate CTFd components or use CTFd as a dependency
- [x] Add user authentication and team management
- [x] Implement challenge creation and solving workflow
- [x] Build a scoreboard with dynamic scoring
- [ ] Support plugins and custom challenge types
