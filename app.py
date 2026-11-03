import pandas as pd 
import math 

from flask import Flask, render_template, jsonify, request 
app = Flask(__name__)
from routing_sparse import generate_route, prepare_routing 
def get_safety_advice(risk_level):
    if risk_level == "High":
        return (
            "Caution: This district has a relatively high "
            "reported-crime burden. Stay alert and identify "
            "nearby help facilities."
        )

    elif risk_level == "Medium":
        return (
            "Stay aware of your surroundings and keep "
            "nearby help facility information accessible."
        )

    else:
        return (
            "Continue following normal safety precautions "
            "and keep nearby help information accessible."
        ) 
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/check-safety")
def check_safety():

    # Load our real mapped facility data
    df = pd.read_csv("data/jalandhar_emergency_points.csv")

    # Starting location for our demonstration
    user_lat = 31.3260
    user_lon = 75.5762

    # Keep hospitals and police facilities
    df = df[df["type"].isin(["hospital", "police"])]

    def calculate_distance(lat1, lon1, lat2, lon2):
        radius = 6371000

        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        a = (
            math.sin((lat2 - lat1) / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin((lon2 - lon1) / 2) ** 2
        )

        return radius * 2 * math.asin(math.sqrt(a))

    # Find the nearest mapped facility
    df["distance"] = df.apply(
        lambda row: calculate_distance(
            user_lat,
            user_lon,
            row["latitude"],
            row["longitude"]
        ),
        axis=1
    )

    nearest = df.loc[df["distance"].idxmin()]

    return jsonify({
        "area": "Jalandhar demonstration location",
        "nearest_help_point": nearest["name"],
        "facility_type": nearest["type"],
        "distance_metres": round(nearest["distance"]),
        "message": "Nearby help information is based on mapped facilities from OpenStreetMap. It does not represent verified crime hotspots."
    })
@app.route("/map")
def show_map():
    return render_template("jalandhar_map.html") 
@app.route("/safe-route")
def safe_route():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if lat is None or lon is None:
        return (
            "Location coordinates are missing. "
            "Please click Find Safe Route from the homepage.",
            400
        )

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return "Invalid location coordinates.", 400

    try:
        result = generate_route(lat, lon)

        return render_template(
            "safe_route.html",
            facility_name=result["facility_name"],
            facility_type=result["facility_type"],
            distance_metres=result["distance_metres"],
            map_filename=result["map_filename"]
        )

    except Exception:
        app.logger.exception("Unable to generate the route")

        return (
            "Unable to generate a route from this location. "
            "Please check that the location is within the "
            "supported Jalandhar road network and try again.",
            500
        ) 
          
@app.route("/crime-analysis")
def crime_analysis():
    import pandas as pd

    df = pd.read_csv("data/jalandhar_crime_summary.csv")

    crime_data = df.to_dict(orient="records")

    return render_template(
        "crime_analysis.html",
        crime_data=crime_data
    ) 
@app.route("/ai-analysis")
def ai_analysis():
    import pandas as pd
    import joblib

    # Load real crime data
    df = pd.read_csv("data/ncrb_crime_data_2022.csv")

    # Find Jalandhar
    district = df[
        df["dis"].astype(str).str.contains(
            "Jalandhar", case=False, na=False
        )
    ]

    if district.empty:
        return "Jalandhar data not found.", 404

    # Load the trained AI model
    saved_model = joblib.load("crime_model.pkl")

    model = saved_model["model"]
    features = saved_model["features"]

    # Prepare Jalandhar's historical crime statistics
    input_data = district[features].apply(
        pd.to_numeric, errors="coerce"
    )

    if input_data.isnull().any().any():
        return "Some historical crime data is missing.", 400

    # Classify the district's reported-crime burden
    prediction = model.predict(input_data)[0]

    return render_template(
        "ai_analysis.html",
        district_name="Jalandhar",
        prediction=str(prediction)
    )  
@app.route("/api/ai-analysis")
def api_ai_analysis():
    import pandas as pd
    import joblib

    df = pd.read_csv("data/ncrb_crime_data_2022.csv")

    district = df[
        df["dis"].astype(str).str.contains(
            "Jalandhar", case=False, na=False
        )
    ]

    if district.empty:
        return {"error": "Jalandhar data not found"}, 404

    saved_model = joblib.load("crime_model.pkl")
    model = saved_model["model"]
    features = saved_model["features"]

    input_data = district[features].apply( 
        pd.to_numeric, errors="coerce"
    )

    if input_data.isnull().any().any():
        return {"error": "Historical data is incomplete"}, 400

    prediction = str(model.predict(input_data)[0])
    advice = get_safety_advice(prediction)

    return {
        "district": "Jalandhar",
        "risk_level": prediction,
        "message": (
            "This is a relative classification of reported "
            "district-level crime burden, not street-level danger."
        ),
        "safety_advice": advice
    }


if __name__ == "__main__":
    prepare_routing()
    app.run(debug=True)  