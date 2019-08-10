# Import dependencies
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Create an engine to communicate with the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references for the two tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create an app
app = Flask(__name__)

# Define routes
@app.route("/")
def home():
    # List all available routes and explain what each one does
    return (
        "Welcome to the Hawaiian Climate API </br>"
        "</br>"
        "</br>"
        "Available Routes: </br>"
        "/api/v1.0/precipitation </br>"
        "Lists the precipitation data from all stations for the lasts 12 months </br>"
        "</br>"
        "/api/v1.0/stations </br>"
        "Lists the station numbers and their names </br>"
        "</br>"
        "/api/v1.0/tobs </br>"
        "Lists the temperature observations from all stations for the last 12 months </br>"
        "</br>"
        "/api/v1.0/start </br>"
        "Lists the MIN/AVG/MAX temperature observations for all dates greater than and equal to the start date (yyyy-mm-dd) </br>"
        "</br>"
        "/api/v1.0/start/end </br>"
        "Lists the MIN/AVG/MAX temperature observations for all dates between the start and end date inclusive (yyyy-mm-dd)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Query for the date and prcp values for the year prior to the last data point
    session = Session(engine)
    last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    first_day = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).\
        filter(Measurement.date > first_day).all()

    # Convert the query results to a dictionary with date as the key and prcp as the value; then append to a list in json
    precipitation_list = []
    for date, prcp in precipitation:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation_list.append(precipitation_dict)
    session.close()

    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations")
def stations():

    # Query for the name and station in the Station table
    session = Session(engine)
    stations = session.query(Station.name, Station.station).all()

    # Convert the query results to a dictionary with name and station as the keys; then append to a list in json
    station_list = []
    for name, station in stations:
        stations_dict = {}
        stations_dict["name"] = name
        stations_dict["station"] = station
        station_list.append(stations_dict)
    session.close()

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():

    # Query for the dates and tobs from a year prior to the last data point
    session = Session(engine)
    first_day = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date).\
    filter(Measurement.date > first_day).all()

    # Convert the query results to a dictionary with date and tobs as the keys; then append to a list in json
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)
    session.close()

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_date(start):

    # Allow the user to enter a date which will query the min, avg, and max for the tobs from the date they enter to 
    # the last data point (2017-08-23)
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_day = dt.date(2017, 8, 23)
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    # Convert the query results to a dictionary with TMIN, TAVG, TMAX as the keys; then append to a list in json
    temp_list = []
    for tobs in temps:
        temps_dict = {}
        temps_dict["TMIN"] = tobs[0]
        temps_dict["TAVG"] = tobs[1]
        temps_dict["TMAX"] = tobs[2]
        temp_list.append(temps_dict)
    session.close()

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_dates(start,end):

    # Allow the user to enter a start date and end date which will query the min, avg, and max for the tobs 
    # from the start date that they enter to the end date that they enter
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Convert the query results to a dictionary with TMIN, TAVG, TMAX as the keys; then append to a list in json
    temps_list = []
    for tobs in temps:
        temps_dict = {}
        temps_dict["TMIN"] = tobs[0]
        temps_dict["TAVG"] = tobs[1]
        temps_dict["TMAX"] = tobs[2]
        temps_list.append(temps_dict)
    session.close()

    return jsonify(temps_list)

# Define main behavior
if __name__ == "__main__":
    app.run(debug=True)    