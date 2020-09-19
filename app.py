import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session 
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start in format Y-m-d<br/>"
        f"/api/v1.0/temp/start/end in format Y-m-d/Y-m-d"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date 1 year ago from last date in database
    max_date = session.query(func.max(Measurement.date)).all()
    m_date = dt.datetime.strptime(max_date[0][0], '%Y-%m-%d')
    min_date = m_date - dt.timedelta(days=366)
    session.close() 

    # Query for the date and precipitation for the last year
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= min_date).\
    order_by(Measurement.date).all()
    session.close() 

    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in results}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    
    station_result = session.query(Station.station).all()
    session.close() 

    stations = list(np.ravel(station_result))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    # Calculate the date 1 year ago from last date in database
    max_date = session.query(func.max(Measurement.date)).all()
    m_date = dt.datetime.strptime(max_date[0][0], '%Y-%m-%d')
    min_date = m_date - dt.timedelta(days=366)
    session.close() 

    # Query the primary station for all tobs from the last year
    temp_result = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= min_date).all()
    session.close() 

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(temp_result))

    # Return the results
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")

def single_date(start):
	# Set up for user to enter date
	Start_Date = dt.datetime.strptime(start,"%Y-%m-%d")
	# Query Min, Max, and Avg based on date
	stats_start = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
	filter(Measurement.date >= Start_Date).all()
	session.close() 
	
	summary = list(np.ravel(stats_start))

	# Jsonify summary
	return jsonify(summary)

@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):

    Start_Date = dt.datetime.strptime(start,"%Y-%m-%d")
    End_Date = dt.datetime.strptime(end,"%Y-%m-%d")
    
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(
        Measurement.tobs), func.max(Measurement.tobs)]
    
    # calculate TMIN, TAVG, TMAX with start and stop
    stat_info = session.query(*sel).filter(Measurement.date >= Start_Date).filter(Measurement.date <= End_Date).all()

    temps = list(np.ravel(stat_info))
    return jsonify(temps=temps)

if __name__ == '__main__':

    app.run(port=9999)