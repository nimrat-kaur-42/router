# Istanbul Route Finder

A web-based visualization tool that compares A\* and Dijkstra pathfinding algorithms on real Istanbul road networks.

## Project Overview

This application demonstrates the practical differences between two classic pathfinding algorithms using real-world data from Istanbul, Turkey. It provides an interactive interface to select routes and visualize how each algorithm explores the network to find the optimal path.

### Key Features

- **Real-World Data**: 700,095 data points from OpenStreetMap (192,588 nodes + 507,507 edges)
- **Interactive Selection**: Choose from 20 Istanbul landmarks or use custom coordinates
- **Side-by-Side Comparison**: Compare A\* and Dijkstra performance metrics
- **Visual Exploration**: See how each algorithm explores the road network
- **Live Results**: Images appear progressively as they're generated

## Technology Stack

- **Backend**: Python Flask
- **Data Processing**: OSMnx, NetworkX
- **Visualization**: Matplotlib
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Source**: OpenStreetMap

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

Installation:
STEP 1: Install Dependencies

---

pip install -r requirements.txt

## STEP 2: Start the Server

python app.py

(First run: 2-3 min download)

## STEP 3: Open Browser

http://localhost:5000

## STEP 4: Use It

1. Select origin
2. Select destination
3. Click "Compute Route Now"
4. Wait for a few minutes
5. See results
