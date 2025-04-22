# Import the dependencies.
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, func, desc
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt
from dateutil.relativedelta import relativedelta

#################################################
# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#################################################


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#get the last date from our table
recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
# Starting from the most recent data point in the database. 
end_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d').date()

# Calculate the date one year from the last date in data set.
start_date = end_date - relativedelta(months=12) 

#################################################
# Flask Setup
app = Flask(__name__)
#################################################




#################################################
# Flask Routes
@app.route("/")
def home():
    return (
        "<b>Welcome to the Climate App.</b><br><br>"
        "Below are the available routes:<br><br>"

        "<b>Last 12 months of precipitation data:</b><br>"
        "<ul><li><a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a></li></ul><br>"

        "<b>List of stations:</b><br>"
        "<ul><li><a href='/api/v1.0/stations'>/api/v1.0/stations</a></li></ul><br>"

        "<b>Temperature observations of the most active station (USC00519281):</b><br>"
        "<ul><li><a href='/api/v1.0/tobs'>/api/v1.0/tobs</a></li></ul><br>"

        "<b>Temperature Data:</b><br>"
        "By a specified start date (YYYY-MM-DD):<br>"
        "<ul><li>/api/v1.0/&lt;start&gt;</a></li></ul><br>"

        "By a specified start date and end date (YYYY-MM-DD):<br>"
        "<ul><li>/api/v1.0/&lt;start&gt;/&lt;end&gt;</a></li></ul>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation_route():
    #retrieve the last 12 months of data
    return jsonify([{"Date": x[0], "Precipitation": x[1]} for x in session.\
                                query(Measurement.date, Measurement.prcp).\
                                filter(Measurement.date >= start_date).\
                                order_by(Measurement.date).\
                                all() ])

@app.route("/api/v1.0/stations")
def stations_route():
    return jsonify([x[0] for x in session.query(Measurement.station).distinct()])

@app.route("/api/v1.0/tobs")
def tobs_route():
    return jsonify([{"Date": x[0], "Temperature": x[1]} for x in session.\
                                query(Measurement.date, Measurement.tobs).\
                                filter(Measurement.date >= start_date, Measurement.station == "USC00519281").\
                                order_by(Measurement.date).\
                                all() ])
@app.route("/api/v1.0/<start>")
def start_route(start):
    try:
        # Validate and convert input to datetime object
        cleaned_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD."

    temp_data = session.query(func.min(Measurement.tobs),\
                              func.max(Measurement.tobs),\
                                func.avg(Measurement.tobs)).\
                                    filter(Measurement.date >= cleaned_date ).all()
    
    temp_min, temp_max, temp_avg = temp_data[0]
    return (
        f"<b>Temperature information for dates starting from {cleaned_date}:</b><br>"
        f"Minimum Temperature: {temp_min}<br>"
        f"Maximum Temperature: {temp_max},<br>"
        f"Average Temperature: {round(temp_avg,2)}"
    )
@app.route("/api/v1.0/<start>/<end>")
def start_end_route(start, end):
    try:
        # Validate and convert input to datetime object
        cleaned_start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
        cleaned_end_date = dt.datetime.strptime(end, "%Y-%m-%d").date()
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD/YYYY-MM-DD."

    temp_data = session.query(func.min(Measurement.tobs),\
                              func.max(Measurement.tobs),\
                                func.avg(Measurement.tobs)).\
                                    filter(Measurement.date >= cleaned_start_date,\
                                           Measurement.date <= cleaned_end_date).all()
    
    temp_min, temp_max, temp_avg = temp_data[0]
    return (
        f"<b>Temperature information for dates starting {cleaned_start_date} and ending {cleaned_end_date}:</b><br>"
        f"Minimum Temperature: {temp_min}<br>"
        f"Maximum Temperature: {temp_max},<br>"
        f"Average Temperature: {round(temp_avg,2)}"
    )

#################################################
if __name__ == "__main__":
    app.run(debug = True)