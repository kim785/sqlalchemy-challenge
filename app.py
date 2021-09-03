# Import
import numpy as np
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from flask import Flask, jsonify, json

##########################
# Database setup
##########################

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

##########################
# Flask setup
##########################

app = Flask(__name__)

##########################
# Flask Routes
##########################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )




@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()
    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def station():
    # Session
    session = Session(engine)

    # Query
    results = session.query(Station.name).all()
    session.close()

    # Return a JSON list of stations from the dataset
    all_station = list(np.ravel(results))
    return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def tobs():
    # Session
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data.
    most_active = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).first()
    most_recent = session.query(Measurement.date).filter(Measurement.station == most_active[0]).order_by(Measurement.date.desc()).first()
    query_date = dt.date(2017, 8, 18) - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active[0]).filter(Measurement.date >= query_date).all()
    session.close()

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    all_tobs = list(np.ravel(results))
    return jsonify(all_tobs)

    # Convert list of tuples into normal list

@app.route("/api/v1.0/<start>")
def startdate(start):
    # Session
    session = Session(engine)
    
    #Query the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    TMIN = session.query(Measurement.date, func.min(Measurement.tobs)).filter(Measurement.date >= start).all()
    TMAX = session.query(Measurement.date, func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    TAVG = session.query(Measurement.date, func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    # Return a JSON list 
    all_temp = list(np.ravel(results))
    return jsonify(all_temp)

@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start, end):
    # Session
    session = Session(engine)
    
    #Query the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    TMIN = session.query(Measurement.date, func.min(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    TMAX = session.query(Measurement.date, func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    TAVG = session.query(Measurement.date, func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    # Return a JSON list 
    all_temp = list(np.ravel(results))
    return jsonify(all_temp)
if __name__ == "__main__":
    app.run(debug=True)