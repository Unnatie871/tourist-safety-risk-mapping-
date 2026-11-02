# Tourist Safety Risk Mapping and Fast-Help Routing Agent

An AI-assisted tourist safety web application designed to help users explore safety information, view crime statistics, locate nearby assistance, and find routes to mapped emergency facilities.

## 📌 Project Overview

Tourists visiting unfamiliar locations may have difficulty understanding local safety conditions and finding appropriate assistance during emergencies.

The **Tourist Safety Risk Mapping and Fast-Help Routing Agent** aims to address this problem through an interactive web application that combines crime-data analysis, machine learning, geographic visualization, and route planning.

The project currently focuses on Jalandhar, Punjab, India.

## 🎯 Objectives

- Present crime-related information in an accessible format.
- Classify safety risk using a machine learning model.
- Display geographic information through interactive maps.
- Help users find routes to mapped hospitals and police facilities.
- Provide an SOS feature that prepares an emergency WhatsApp message containing the user's current location.

## ✨ Key Features

### 1. Crime Analysis
Displays available crime-related information to help users understand the data used by the application.

### 2. AI-Based Risk Classification
Uses a Random Forest classification model to classify risk based on the features available in the project's dataset.

### 3. Interactive Safety Map
Uses Folium and OpenStreetMap-based geographic data to visualize mapped locations.

### 4. Emergency Route Planning
Uses road-network data and graph algorithms to find a route from the user's location to a mapped help facility.

### 5. Emergency SOS
Allows a user to enter a trusted contact's Indian mobile number and prepare an emergency WhatsApp message containing a Google Maps link to their current location.

The user must review and send the message through WhatsApp. The feature does not automatically contact the police or emergency services.

## 🛠️ Technologies Used

- **Programming Language:** Python
- **Backend Framework:** Flask
- **Frontend:** HTML, CSS, JavaScript
- **Data Processing:** Pandas
- **Machine Learning:** Scikit-learn
- **Interactive Maps:** Folium
- **Geographic Data and Road Networks:** OpenStreetMap and OSMnx
- **Graph Processing and Routing:** NetworkX and A* search
- **Location Services:** Browser Geolocation API
- **Messaging:** WhatsApp click-to-chat link

## 🧠 How It Works

1. The user opens the web application.
2. The user accesses crime analysis and AI-based risk classification.
3. Interactive maps display available geographic information.
4. When route planning is requested, the application uses the user's browser location and the available road network to calculate a route to a mapped help facility.
5. When SOS is activated, the browser requests location permission and prepares a WhatsApp message with a Google Maps location link.

## 📂 Project Structure

```text
tourist_safety/
├── app.py
├── routing.py
├── train_model.py
├── prepare_road_network.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
├── static/
└── data/
```

*Note: The actual repository may contain additional files and folders.*

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10 or a compatible version supported by the project's dependencies.
- pip package manager.
- Git, if you want to clone the repository.
- An internet connection for downloading geographic data and using relevant map services.

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd tourist-safety-risk-mapping
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with the repository's actual URL.

### 2. Create a virtual environment

On Windows:

```bash
py -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare the road network

If the road-network file is not already available, run:

```bash
py prepare_road_network.py
```

This downloads and saves the Jalandhar road network. It may take some time and requires an internet connection.

### 5. Start the application

```bash
py app.py
```

Open the local address printed by Flask in your browser. By default, this is usually:

```text
http://127.0.0.1:5000
```

## ⚠️ Important Limitations

- The application currently focuses on Jalandhar, Punjab.
- Risk classifications depend on the available dataset and the model's training process.
- District-level crime statistics do not establish whether a particular street is safe.
- Mapped facilities may not be open, available, or equipped to handle every emergency.
- Route quality depends on the available road-network data.
- Browser location access requires user permission and an appropriate browser context.
- The SOS feature prepares a WhatsApp message but requires the user to send it manually.
- The application should not replace official emergency services or local safety advice.

## 🔮 Future Enhancements

- Expand geographic coverage to additional cities.
- Improve risk predictions using reliable, updated datasets.
- Add a more comprehensive emergency-contact management system.
- Integrate a properly configured messaging service for supported emergency notifications.
- Improve route evaluation using verified facility information and additional safety criteria.
- Develop a mobile application.
- Deploy the system on a publicly accessible hosting platform.

