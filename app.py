import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from datetime import datetime

# create engine for the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# reference for each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# create session link
session = Session(engine)

# create an app
app = Flask(__name__)

# define index route
@app.route("/")
def home():
    return(
    f"Climate Archive, Honolulu, Hawaii<br/>"
    f"Available Routes:<br/>"
    f"<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"Return results of date and precipitation: <br/>"
    f"<br/>"
    f"/api/v1.0/stations<br/>"
    f"Return a JSON list of stations from the dataset: <br/>"
    f"<br/>"
    f"/api/v1.0/tobs<br/>"
    f"Return a list of Temperature Observations (tobs) for the previous year: <br/>"
    f"<br/>"
    f"/api/v1.0/start/<br/>"
    f"Return a list of the minimum temperature, the average temperature, and the max temperature for all dates equal or after the input date <br/>"
    f" for example: /api/v1.0/2014-01-01 <br/>"
    f"<br/>"
    f"/api/v1.0/start/end<br/>"
    f"Return a list of the minimum temperature, the average temperature, and the max temperature for dates between the start and end date inclusive <br/>"
    f" for example: /api/v1.0/2014-01-01/2014-01-30 <br/>"
    )

# Return a JSON list of date and precipitation from station USC00519281

app.route("/api/v1.0/precipitation")   
def precipitation():
    all_prcps = []
    results = session.query(Measurement.date, Measurement.prcp).all()
    for date, prcp in results:
        all_prcps.append({date: prcp})
    return jsonify(all_prcps)

# Return a list of stations from the dataset.
@app.route("/api/v1.0/stations")   
def stations():
    results = session.query(Station.station).all()
    all_station = list(np.ravel(results))
    return jsonify(all_station)

# Return a JSON list of Temperature Observations (tobs) for the previous year.    
@app.route("/api/v1.0/tobs")   
def tobs():
    # checking the date a year from the last data point
    last_date = session.query(func.max(Measurement.date)).all()[0][0]
    first_date = datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days = 365)
    results = session.query(Measurement.tobs).\
                  filter(Measurement.date <= last_date).\
                  filter(Measurement.date >= first_date).\
                  order_by(Measurement.date).all()
    all_tobs = list(np.ravel(results)) 
    return jsonify(all_tobs)          

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
# for all dates equal or after the input <start> date
@app.route("/api/v1.0/<start>") 
def climate_start(start):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results =  session.query(*sel).filter(Measurement.date >= start).all()
    after_start_tobs = list(np.ravel(results)) 
    return jsonify(after_start_tobs)  

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
# for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>") 
def climate_between(start, end):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results =  session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    between_tobs = list(np.ravel(results)) 
    return jsonify(between_tobs)  

if __name__ == "__main__":
    app.run(debug=True)
