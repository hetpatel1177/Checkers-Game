# Checkers Game

A **web-based checkers game** where you can play against an AI opponent on a classic 8×8 board. Built using **React** (frontend) and **Python Flask** (backend), this project aims to provide a fun and interactive way to play checkers directly in your browser.

---
<img width="868" height="705" alt="Screenshot 2025-07-17 at 1 28 39 PM" src="https://github.com/user-attachments/assets/cc87fe5c-13cb-4659-bece-42973fc0faca" />


## Features

- **Play against AI:** Challenge a computer opponent with built-in move logic and minimax strategy.
- **Simple, clean interface:** Intuitive UI powered by React and styled with TailwindCSS and custom CSS.
- **Move history:** Track each player's moves in a sidebar.
- **Name entry:** Personalize your game by entering your name before starting.
- **Game rules reference:** Read clear rules and objectives alongside the board.
- **Automatic kinging:** Pieces are promoted when reaching the opposite end.
- **Reset functionality:** Start a new game with one click.
- **Responsive design:** Looks great on desktop browsers.

## Tech Stack

| Frontend          | Backend            | Styling            |
|-------------------|--------------------|--------------------|
| React, JSX        | Python, Flask      | Tailwind CSS, CSS  |

## Project Structure

- **/App.jsx** — Main React application, state management, move logic, communicates with backend[2].
- **/App.css, /index.css** — Custom and Tailwind-based styling for board and UI[1][3].
- **/main.jsx** — Entry point for React app[4].
- **/app.py** — Flask server API, endpoints for game board, move logic, reset[5].
- **/checkers.py** — Core checkers game logic and rules, including AI with minimax algorithm[6].

<img width="368" height="565" alt="Screenshot 2025-07-17 at 2 18 18 PM" src="https://github.com/user-attachments/assets/4545ba44-2f59-4360-9500-e1fe08533c3d" />

## Getting Started

1. **Clone the repository**
git clone https://github.com/hetpatel1177/Checkers-Game.git
cd Checkers-Game

2. **Install frontend dependencies**
npm install

3. **Install backend dependencies**
pip install flask flask-cors

4. **Start the backend**
python app.py
The Flask backend will start on `localhost:5000` by default.

5. **Start the frontend**
npm run dev
Visit `http://localhost:5173` in your browser (adjust if needed).

## Game Rules

- **Pieces** move diagonally forward by 1 square; they capture by jumping over opponent pieces.
- **Kinging**: Reach the opponent’s back row to become a King (can move and capture both directions).
- **Objective**: Capture or block all of your opponent’s pieces.
- **Draw**: Game drawn if same board position repeats 5 times with the same player's move[6].
- **Both normal and king pieces visibly indicated on the board.**

## Customization

- Edit **checkers.py** to adjust AI difficulty (minimax depth).
- Modify **App.css** and **index.css** for custom board themes.

## License

MIT License

---

For suggestions or issues, please open an issue in this repo!
