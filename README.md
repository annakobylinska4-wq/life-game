# Life Game - Jones in the Fast Lane Style

A simple web-based life simulation game inspired by "Jones in the Fast Lane".

## Features

- **User Authentication**: Register and login with credentials stored in local JSON files
- **Turn-based Gameplay**: Make choices each turn to progress through life
- **4 Locations**:
  - 🎓 **University**: Study to improve qualifications (costs $50)
  - 💼 **Job Office**: Find a job based on your qualifications
  - 🏢 **Workplace**: Work at your current job to earn money
  - 🛒 **Shop**: Buy items with your money

## Game Mechanics

- Start with $100
- Better qualifications = better jobs = higher wages
- Progression: None → High School → Bachelor → Master → PhD
- Jobs range from Janitor ($20/turn) to Executive ($150/turn)
- Buy items like Food, Clothes, Phone, Laptop, Car

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and go to:
```
http://localhost:5000
```

## How to Play

1. Register a new account or login
2. View your current status (money, job, qualifications, items)
3. Each turn, choose one location to visit:
   - Study at University to improve qualifications
   - Visit Job Office to get a better job
   - Go to Workplace to earn money
   - Shop to buy items
4. Watch your status change and try to improve your life!

## Technology Stack

- **Backend**: Python with Flask
- **Frontend**: Plain HTML, CSS, and JavaScript (no frameworks)
- **Storage**: JSON flat files (no database)
- **Authentication**: Simple password hashing with local file storage

## File Structure

```
life_game/
├── app.py              # Flask backend server
├── requirements.txt    # Python dependencies
├── data/               # Game data storage
│   ├── users.json      # User credentials
│   └── game_states.json # Player game states
├── static/             # Frontend assets
│   ├── style.css       # Styling
│   └── game.js         # Client-side JavaScript
└── templates/          # HTML templates
    └── index.html      # Main game page
```

## Notes

- All user data is stored locally in JSON files
- No external database required
- No Node.js or modern frontend frameworks
- Simple and self-contained
